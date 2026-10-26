from django.conf import settings
from django.db import models

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120, blank=True)
    education = models.CharField(max_length=160, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills, e.g. Python, SQL, Django")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    def skill_list(self):
        return [s.strip().lower() for s in self.skills.split(",") if s.strip()]

    def __str__(self):
        return self.full_name or self.user.username

class Internship(models.Model):
    title = models.CharField(max_length=160)
    company = models.CharField(max_length=160)
    location = models.CharField(max_length=120, default="Remote")
    description = models.TextField(blank=True)
    required_skills = models.TextField(help_text="Comma-separated skills")
    application_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def skill_list(self):
        return [s.strip().lower() for s in self.required_skills.split(",") if s.strip()]

    def __str__(self):
        return f"{self.title} — {self.company}"

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    extracted_skills = models.TextField(blank=True)
    extracted_text_preview = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160)
    issue_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="certificates/", blank=True)
    sha256_hash = models.CharField(max_length=64, blank=True, db_index=True)
    blockchain_mode = models.CharField(max_length=30, default="local-demo")
    transaction_hash = models.CharField(max_length=100, blank=True)
    chain_record_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} — {self.user.username}"
