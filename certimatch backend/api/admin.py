from django.contrib import admin
from .models import Certificate, ExtractedSkill, JobListing, JobApplication, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'full_name', 'created_at']
    search_fields = ['user__email', 'full_name']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display  = ['user', 'original_filename', 'status', 'uploaded_at']
    search_fields = ['user__email', 'original_filename']
    list_filter   = ['status']

@admin.register(ExtractedSkill)
class ExtractedSkillAdmin(admin.ModelAdmin):
    list_display  = ['skill_name', 'certificate', 'confidence']
    search_fields = ['skill_name', 'certificate__user__email']

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display  = ['job_title', 'company', 'salary_lpa']
    search_fields = ['job_title', 'company']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'job', 'status', 'applied_at']
    search_fields = ['user__email', 'job__job_title']
    list_filter   = ['status']
