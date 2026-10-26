from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("resume/analyze/", views.analyze_resume, name="analyze_resume"),
    path("internships/", views.internships, name="internships"),
    path("certificates/", views.certificates, name="certificates"),
    path("certificates/<int:certificate_id>/verify/", views.verify_certificate, name="verify_certificate"),
    path("verify/", views.public_verify, name="public_verify"),
]
