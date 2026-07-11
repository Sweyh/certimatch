from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'extracted_skills', 'uploaded_at']
    search_fields = ['user__email', 'title']
