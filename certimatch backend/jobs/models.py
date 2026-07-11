from django.db import models
from django.conf import settings


class Job(models.Model):
    title           = models.CharField(max_length=255)
    company         = models.CharField(max_length=255)
    location        = models.CharField(max_length=255, default='Remote')
    skills_required = models.TextField()     # comma-separated
    salary_lpa      = models.FloatField(default=0.0)
    salary_rupees   = models.FloatField(default=0.0)

    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied',    'Applied'),
        ('shortlisted','Shortlisted'),
        ('rejected',   'Rejected'),
    ]
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='applications')
    job        = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.email} → {self.job.title}"
