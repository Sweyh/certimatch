from django.db import models
from django.conf import settings


class Certificate(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='certificates')
    title       = models.CharField(max_length=255)          # e.g. "AWS Cloud Practitioner"
    file        = models.FileField(upload_to='certificates/%Y/%m/')
    extracted_skills = models.TextField(blank=True)          # comma-separated skills
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def skills_list(self):
        return [s.strip() for s in self.extracted_skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.user.email} — {self.title}"
