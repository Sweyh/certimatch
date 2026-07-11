from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Certificate, ExtractedSkill, JobListing, JobApplication

User = get_user_model()


# ─── Auth ─────────────────────────────────────────────────────────────────────

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True, required=False, default='')

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email is already registered.'})
        return data

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        UserProfile.objects.create(user=user, full_name=full_name)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# ─── Skills ──────────────────────────────────────────────────────────────────

class ExtractedSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedSkill
        fields = ['id', 'skill_name', 'confidence']


# ─── Certificate ─────────────────────────────────────────────────────────────

class CertificateSerializer(serializers.ModelSerializer):
    skills = ExtractedSkillSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'original_filename', 'status', 'uploaded_at', 'skills']


# ─── Jobs ────────────────────────────────────────────────────────────────────

class JobListingSerializer(serializers.ModelSerializer):
    skills_list = serializers.SerializerMethodField()
    match_score = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()

    class Meta:
        model = JobListing
        fields = [
            'id', 'job_title', 'company', 'skills_required',
            'skills_list', 'salary_lpa', 'salary_rupees',
            'match_score', 'missing_skills',
        ]

    def get_skills_list(self, obj):
        return obj.skills_list()

    def get_match_score(self, obj):
        user_skills = self.context.get('user_skills', [])
        if not user_skills:
            return 0
        required = obj.skills_list()
        if not required:
            return 0
        matched = [s for s in required if s.lower() in [u.lower() for u in user_skills]]
        return round(len(matched) / len(required) * 100)

    def get_missing_skills(self, obj):
        user_skills = self.context.get('user_skills', [])
        required = obj.skills_list()
        return [s for s in required if s.lower() not in [u.lower() for u in user_skills]]


# ─── Applications ────────────────────────────────────────────────────────────

class JobApplicationSerializer(serializers.ModelSerializer):
    job = JobListingSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=JobListing.objects.all(), source='job', write_only=True
    )

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_id', 'status', 'applied_at']
