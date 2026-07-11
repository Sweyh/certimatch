from rest_framework import serializers
from .models import Job, Application


class JobSerializer(serializers.ModelSerializer):
    skills_list  = serializers.ReadOnlyField()
    match_score  = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()

    class Meta:
        model  = Job
        fields = ['id', 'title', 'company', 'location',
                  'skills_required', 'skills_list',
                  'salary_lpa', 'salary_rupees',
                  'match_score', 'missing_skills']

    def get_match_score(self, obj):
        user_skills = self.context.get('user_skills', [])
        if not user_skills:
            return 0
        required = obj.skills_list()
        if not required:
            return 100
        matched = [s for s in required if s in user_skills]
        return round(len(matched) / len(required) * 100)

    def get_missing_skills(self, obj):
        user_skills = self.context.get('user_skills', [])
        return [s for s in obj.skills_list() if s not in user_skills]


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model  = Application
        fields = ['id', 'job', 'status', 'applied_at']
