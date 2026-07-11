from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Certificate
from .serializers import CertificateSerializer
from .skill_extractor import extract_skills_from_title


class CertificateListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certs = Certificate.objects.filter(user=request.user).order_by('-uploaded_at')
        return Response(CertificateSerializer(certs, many=True).data)

    def post(self, request):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            title  = serializer.validated_data['title']
            skills = extract_skills_from_title(title)
            cert   = serializer.save(user=request.user, extracted_skills=skills)
            return Response(CertificateSerializer(cert).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Certificate.objects.get(pk=pk, user=user)
        except Certificate.DoesNotExist:
            return None

    def get(self, request, pk):
        cert = self.get_object(pk, request.user)
        if not cert:
            return Response({'error': 'Not found'}, status=404)
        return Response(CertificateSerializer(cert).data)

    def delete(self, request, pk):
        cert = self.get_object(pk, request.user)
        if not cert:
            return Response({'error': 'Not found'}, status=404)
        cert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllSkillsView(APIView):
    """Returns a flat list of all unique skills the logged-in user has."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certs = Certificate.objects.filter(user=request.user)
        skills = set()
        for cert in certs:
            skills.update(cert.skills_list())
        return Response({'skills': sorted(skills)})
