from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer
from .ml_matcher import get_top_matches
from certificates.models import Certificate


def _get_user_skills(user):
    """Collect all unique skills from user's certificates."""
    certs = Certificate.objects.filter(user=user)
    skills = set()
    for cert in certs:
        skills.update(cert.skills_list())
    return list(skills)


# ── Job Listing ────────────────────────────────────────────────────────────────

class JobListView(APIView):
    """All jobs from DB, annotated with match score for the logged-in user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_skills = _get_user_skills(request.user)
        jobs = Job.objects.all().order_by('title')
        serializer = JobSerializer(jobs, many=True, context={'user_skills': user_skills})
        return Response(serializer.data)


# ── ML-powered Matches ─────────────────────────────────────────────────────────

class MLMatchView(APIView):
    """
    Uses the TF-IDF model to find best job matches from the 10k-row dataset.
    GET /api/jobs/matches/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_skills = _get_user_skills(request.user)
        if not user_skills:
            return Response({'error': 'No certificates uploaded yet. Please upload a certificate first.'}, status=400)
        matches = get_top_matches(user_skills, top_n=10)
        return Response({'user_skills': user_skills, 'matches': matches})


# ── Skill Gap ──────────────────────────────────────────────────────────────────

class SkillGapView(APIView):
    """
    GET /api/jobs/skillgap/?role=Data+Scientist
    Returns missing skills and suggested learning resources.
    """
    permission_classes = [IsAuthenticated]

    COURSE_MAP = {
        'Python':           'https://www.udemy.com/course/complete-python-bootcamp/',
        'Machine Learning': 'https://www.coursera.org/learn/machine-learning',
        'Deep Learning':    'https://www.coursera.org/specializations/deep-learning',
        'SQL':              'https://www.coursera.org/learn/sql-for-data-science',
        'TensorFlow':       'https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning/',
        'Docker':           'https://www.udemy.com/course/docker-mastery/',
        'AWS':              'https://aws.amazon.com/training/',
        'Azure':            'https://learn.microsoft.com/en-us/training/azure/',
        'React':            'https://www.udemy.com/course/the-complete-react-native-and-redux-course/',
        'Django':           'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/',
        'Blockchain':       'https://www.udemy.com/course/blockchain-and-bitcoin-fundamentals/',
        'NLP':              'https://www.coursera.org/specializations/natural-language-processing',
    }

    def get(self, request):
        role = request.query_params.get('role', '').strip()
        if not role:
            return Response({'error': 'Provide ?role=<job_title>'}, status=400)

        # Find matching job in DB (case-insensitive)
        job = Job.objects.filter(title__icontains=role).first()
        if not job:
            return Response({'error': f'No job found matching "{role}"'}, status=404)

        user_skills   = _get_user_skills(request.user)
        required      = job.skills_list()
        missing       = [s for s in required if s not in user_skills]
        has_all       = len(missing) == 0

        courses = [
            {'skill': skill, 'course_url': self.COURSE_MAP.get(skill, 'https://www.udemy.com')}
            for skill in missing
        ]

        return Response({
            'role':          job.title,
            'user_skills':   user_skills,
            'required':      required,
            'missing':       missing,
            'eligible':      has_all,
            'courses':       courses,
        })


# ── Salary Predictor ───────────────────────────────────────────────────────────

class SalaryPredictView(APIView):
    """
    POST /api/jobs/salary/
    Body: { "role": "Data Scientist", "experience_years": 2, "location": "Bangalore" }
    """
    permission_classes = [IsAuthenticated]

    LOCATION_FACTOR = {
        'bangalore': 1.20,
        'hyderabad': 1.15,
        'mumbai':    1.25,
        'delhi':     1.18,
        'chennai':   1.10,
        'pune':      1.08,
        'remote':    1.05,
    }

    def post(self, request):
        role        = request.data.get('role', '')
        exp         = float(request.data.get('experience_years', 0))
        location    = request.data.get('location', 'Remote').lower()
        user_skills = _get_user_skills(request.user)

        # Find salary from model dataset
        from django.conf import settings
        import pickle
        with open(settings.ML_MODEL_PATH, 'rb') as f:
            m = pickle.load(f)
        df = m['df']
        matches = df[df['job_title'].str.lower().str.contains(role.lower())]

        if matches.empty:
            base_salary = 6.0
        else:
            base_salary = float(matches['salary_lpa'].mean())

        # Experience multiplier
        exp_multiplier = 1 + (exp * 0.08)
        loc_factor     = self.LOCATION_FACTOR.get(location, 1.0)
        skill_bonus    = len(user_skills) * 0.15

        predicted = round((base_salary + skill_bonus) * exp_multiplier * loc_factor, 2)

        return Response({
            'role':             role,
            'experience_years': exp,
            'location':         location,
            'user_skills_count': len(user_skills),
            'predicted_salary_lpa':    predicted,
            'predicted_salary_rupees': round(predicted * 92000, 0),
        })


# ── Applications ───────────────────────────────────────────────────────────────

class ApplyJobView(APIView):
    """POST /api/jobs/<id>/apply/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)

        app, created = Application.objects.get_or_create(user=request.user, job=job)
        if not created:
            return Response({'message': 'Already applied'}, status=200)
        return Response(ApplicationSerializer(app).data, status=201)


class MyApplicationsView(APIView):
    """GET /api/jobs/applications/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apps = Application.objects.filter(user=request.user).select_related('job')
        return Response(ApplicationSerializer(apps, many=True).data)
