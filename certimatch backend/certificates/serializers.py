from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    skills_list = serializers.ReadOnlyField()

    class Meta:
        model  = Certificate
        fields = ['id', 'title', 'file', 'extracted_skills', 'skills_list', 'uploaded_at']
        read_only_fields = ['extracted_skills', 'uploaded_at']
