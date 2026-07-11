"""
views.py — CertiMatch API
"""
import os
import logging

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status

User = get_user_model()
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Certificate, ExtractedSkill, JobListing, JobApplication
from .serializers import (
    SignupSerializer, LoginSerializer,
    CertificateSerializer, JobListingSerializer, JobApplicationSerializer,
)
from .ml_service import extract_skills_from_text, predict_salary, get_skill_gap

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    ser = SignupSerializer(data=request.data)
    if ser.is_valid():
        user  = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message':   'Account created successfully.',
            'token':     token.key,
            'email':     user.email,
            'full_name': user.profile.full_name,
        }, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    ser = LoginSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=ser.validated_data['email'], password=ser.validated_data['password'])
    if user is None:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)

    full_name = ''
    if hasattr(user, 'profile') and getattr(user.profile, 'full_name', '').strip():
        full_name = user.profile.full_name
    elif getattr(user, 'name', '').strip():
        full_name = user.name
    else:
        full_name = user.email

    return Response({
        'message':   'Login successful.',
        'token':     token.key,
        'email':     user.email,
        'full_name': full_name,
        'is_admin':  user.is_staff,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    all_skills = list(
        ExtractedSkill.objects.filter(certificate__user=user)
        .values_list('skill_name', flat=True).distinct()
    )

    full_name = ''
    if hasattr(user, 'profile') and getattr(user.profile, 'full_name', '').strip():
        full_name = user.profile.full_name
    elif getattr(user, 'name', '').strip():
        full_name = user.name
    else:
        full_name = user.email

    return Response({
        'email':              user.email,
        'full_name':          full_name,
        'certificates_count': user.certificates.count(),
        'skills':             all_skills,
        'applications_count': user.applications.count(),
        'is_admin':           user.is_staff,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    if not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all().order_by('-created_at')
    results = []
    for user in users:
        results.append({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'is_admin': user.is_staff,
            'created_at': user.created_at,
            'certificates_count': user.certificates.count(),
            'applications_count': user.applications.count(),
        })

    return Response({
        'count': len(results),
        'results': results,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_certificate(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed:
        return Response({'error': 'Only PDF, JPG, PNG allowed.'}, status=status.HTTP_400_BAD_REQUEST)

    cert = Certificate.objects.create(
        user=request.user, file=file,
        original_filename=file.name, status='pending',
    )

    extracted_text = ''
    skills = []

    try:
        ext = os.path.splitext(file.name)[1].lower()

        # ── PDF extraction ────────────────────────────────────────
        if ext == '.pdf':
            try:
                import fitz
                doc = fitz.open(cert.file.path)
                for page in doc:
                    extracted_text += page.get_text()
                logger.info(f"PyMuPDF extracted {len(extracted_text)} characters from PDF")
            except ImportError:
                logger.warning("PyMuPDF not available, trying pdfplumber...")
                try:
                    import pdfplumber
                    with pdfplumber.open(cert.file.path) as pdf:
                        for page in pdf.pages:
                            extracted_text += (page.extract_text() or '')
                    logger.info(f"pdfplumber extracted {len(extracted_text)} characters from PDF")
                except ImportError:
                    logger.warning("pdfplumber not available, skipping PDF extraction")

        # ── Image extraction (OCR) ────────────────────────────────
        elif ext in ['.jpg', '.jpeg', '.png']:
            try:
                from PIL import Image
                import pytesseract
                extracted_text = pytesseract.image_to_string(Image.open(cert.file.path))
                logger.info(f"pytesseract extracted {len(extracted_text)} characters from image")
            except ImportError:
                logger.warning("pytesseract not available, trying filename extraction...")
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")

        # ── NLP skill extraction from text ────────────────────────
        if extracted_text.strip():
            skills = extract_skills_from_text(extracted_text)
            logger.info(f"NLP extracted {len(skills)} skills from text: {skills}")

        # ── Fallback: use filename keywords if NLP found nothing ──
        if not skills:
            fn = file.name.lower()
            logger.info(f"No skills from NLP, trying filename extraction from: {file.name}")
            # Map filename keywords → skills
            FILENAME_MAP = [
                ('python',          'Python'),
                ('php',             'PHP'),
                ('mysql',           'MySQL'),
                ('html',            'HTML'),
                ('css',             'CSS'),
                ('javascript',      'JavaScript'),
                ('cpp',             'C++'),
                ('c++',             'C++'),
                ('advanced_cpp',    'C++'),
                ('c_programming',   'C'),
                ('c_prog',          'C'),
                ('java',            'Java'),
                ('react',           'React'),
                ('django',          'Django'),
                ('sql',             'SQL'),
                ('data',            'Data Analysis'),
                ('ml',              'Machine Learning'),
                ('machine',         'Machine Learning'),
                ('cloud',           'AWS'),
                ('aws',             'AWS'),
                ('web',             'Web Development'),
                ('blockchain',      'Blockchain'),
                ('node',            'Node.js'),
                ('angular',         'Angular'),
                ('flutter',         'Flutter'),
                ('kotlin',          'Kotlin'),
                ('swift',           'Swift'),
                ('wd101',           'Web Development'),
                ('wd201',           'Django'),
                ('wd301',           'React'),
            ]
            for keyword, skill in FILENAME_MAP:
                if keyword in fn and skill not in skills:
                    skills.append(skill)

            logger.info(f"Fallback filename extraction: {skills} from {file.name}")

        # ── If still no skills and no text extract, mark as failed ──
        if not skills:
            if not extracted_text.strip():
                logger.warning("No text extracted from certificate - cannot determine skills")
                cert.status = 'failed'
                cert.save()
                return Response({
                    'error': 'Could not extract text from certificate. Ensure file quality is good.',
                    'certificate_id': cert.id,
                }, status=status.HTTP_400_BAD_REQUEST)

        # ── Save skills to DB (avoid duplicates per certificate) ──
        existing_in_cert = set()
        for skill_name in skills:
            if skill_name not in existing_in_cert:
                ExtractedSkill.objects.create(certificate=cert, skill_name=skill_name)
                existing_in_cert.add(skill_name)

        cert.status = 'processed'
        cert.save()

    except Exception as e:
        logger.error(f"Skill extraction failed: {e}", exc_info=True)
        cert.status = 'failed'
        cert.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message':        'Certificate uploaded and skills extracted.',
        'certificate_id': cert.id,
        'skills':         skills,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_certificates(request):
    certs = Certificate.objects.filter(user=request.user).order_by('-uploaded_at')
    return Response(CertificateSerializer(certs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def certificate_detail(request, pk):
    try:
        cert = Certificate.objects.get(pk=pk, user=request.user)
    except Certificate.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    return Response(CertificateSerializer(cert).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    qs = JobListing.objects.all()
    if request.query_params.get('search'):
        qs = qs.filter(job_title__icontains=request.query_params['search'])
    if request.query_params.get('company'):
        qs = qs.filter(company__icontains=request.query_params['company'])
    if request.query_params.get('min_salary'):
        qs = qs.filter(salary_lpa__gte=float(request.query_params['min_salary']))
    if request.query_params.get('max_salary'):
        qs = qs.filter(salary_lpa__lte=float(request.query_params['max_salary']))
    
    user_skills = list(
        ExtractedSkill.objects.filter(certificate__user=request.user)
        .values_list('skill_name', flat=True).distinct()
    )
    
    jobs = list(qs[:50])
    return Response({'count': len(jobs), 'results': JobListingSerializer(jobs, many=True, context={'user_skills': user_skills}).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_jobs(request):
    # Get skills from user's uploaded certificates
    user_skills = list(
        ExtractedSkill.objects.filter(certificate__user=request.user)
        .values_list('skill_name', flat=True).distinct()
    )

    if not user_skills:
        return Response({
            'message': 'No skills found. Please upload a certificate first.',
            'user_skills': [], 'count': 0, 'results': [],
        })

    user_lower = [s.lower().strip() for s in user_skills]
    scored = []

    for job in JobListing.objects.all():
        required = [s.strip() for s in job.skills_required.split(',') if s.strip()]
        if not required:
            continue
        required_lower = [r.lower() for r in required]
        
        # Better matching: check if skill is in user skills (flexible matching)
        matched = []
        for req_skill in required_lower:
            for user_skill in user_lower:
                if req_skill == user_skill or req_skill in user_skill or user_skill in req_skill:
                    matched.append(req_skill)
                    break
        
        missing = [r for r in required_lower if r not in matched]
        score = round(len(matched) / len(required) * 100, 1) if required else 0
        
        scored.append({
            'id':              job.id,
            'job_title':       job.job_title,
            'company':         job.company,
            'skills_required': job.skills_required,
            'skills_list':     required,
            'salary_lpa':      job.salary_lpa,
            'salary_rupees':   job.salary_rupees,
            'match_score':     score,
            'missing_skills':  missing,
            'matched_skills':  matched,
        })

    scored.sort(key=lambda x: x['match_score'], reverse=True)
    return Response({'user_skills': user_skills, 'count': len(scored[:10]), 'results': scored[:10]})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_job(request, pk):
    try:
        job = JobListing.objects.get(pk=pk)
    except JobListing.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=404)
    app, created = JobApplication.objects.get_or_create(user=request.user, job=job)
    if not created:
        return Response({'message': 'Already applied.'})
    return Response({'message': f'Applied to {job.job_title} at {job.company}!', 'application_id': app.id}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications(request):
    apps = JobApplication.objects.filter(user=request.user).select_related('job').order_by('-applied_at')
    user_skills = list(ExtractedSkill.objects.filter(certificate__user=request.user).values_list('skill_name', flat=True).distinct())
    data = [{'application_id': a.id, 'status': a.status, 'applied_at': a.applied_at,
             'job': JobListingSerializer(a.job, context={'user_skills': user_skills}).data} for a in apps]
    return Response({'count': len(data), 'results': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_salary_view(request):
    role       = request.data.get('role', '')
    skills_raw = request.data.get('skills', [])
    experience = int(request.data.get('experience', 0))
    location   = request.data.get('location', '')
    if not role:
        return Response({'error': 'role is required.'}, status=400)
    skills = [s.strip() for s in skills_raw.split(',')] if isinstance(skills_raw, str) else list(skills_raw)
    
    # If no skills provided, get user's skills from certificates
    if not skills:
        skills = list(ExtractedSkill.objects.filter(certificate__user=request.user).values_list('skill_name', flat=True).distinct())
    
    return Response(predict_salary(role, skills, experience, location))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_skill_gap(request):
    target_role = request.data.get('target_role', '')
    if not target_role:
        return Response({'error': 'target_role is required.'}, status=400)
    
    user_skills = list(ExtractedSkill.objects.filter(certificate__user=request.user).values_list('skill_name', flat=True).distinct())
    result = get_skill_gap(user_skills, target_role)
    result['user_skills'] = user_skills
    return Response(result)
