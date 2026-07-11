from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """Extended profile linked to auth user model."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}"


class Certificate(models.Model):
    """A certificate uploaded by a user."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    file = models.FileField(upload_to='certificates/')
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.original_filename}"


class ExtractedSkill(models.Model):
    """Skills extracted from a certificate."""
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    confidence = models.FloatField(default=1.0)  # 0.0 - 1.0

    def __str__(self):
        return self.skill_name


class JobListing(models.Model):
    """Job listing loaded from the ML model's dataset."""
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    skills_required = models.TextField()   # comma-separated
    salary_lpa = models.FloatField()
    salary_rupees = models.FloatField()

    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def __str__(self):
        return f"{self.job_title} @ {self.company}"


class JobApplication(models.Model):
    """Track which user applied to which job."""
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.email} → {self.job.job_title}"
