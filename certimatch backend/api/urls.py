from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('auth/signup/',    views.signup,  name='signup'),
    path('auth/login/',     views.login,   name='login'),
    path('auth/logout/',    views.logout,  name='logout'),
    path('auth/me/',        views.me,      name='me'),
    path('admin/users/',    views.admin_users, name='admin_users'),

    # ── Certificates ──────────────────────────────────────
    path('certificates/upload/',       views.upload_certificate, name='upload_certificate'),
    path('certificates/',              views.list_certificates,  name='list_certificates'),
    path('certificates/<int:pk>/',     views.certificate_detail, name='certificate_detail'),

    # ── Jobs ──────────────────────────────────────────────
    path('jobs/',                      views.list_jobs,          name='list_jobs'),
    path('jobs/recommendations/',      views.recommended_jobs,   name='recommended_jobs'),
    path('jobs/<int:pk>/apply/',       views.apply_job,          name='apply_job'),
    path('jobs/applications/',         views.my_applications,    name='my_applications'),

    # ── Salary ────────────────────────────────────────────
    path('salary/predict/',            views.predict_salary_view, name='predict_salary'),

    # ── Skill Gap ─────────────────────────────────────────
    path('skillgap/analyze/',          views.analyze_skill_gap,  name='analyze_skill_gap'),
]
