from django.contrib import admin
from .models import StudentProfile, Internship, ResumeAnalysis, Certificate

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "education")

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "company", "required_skills")

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("user", "filename", "created_at")

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "user", "blockchain_mode", "is_registered")
