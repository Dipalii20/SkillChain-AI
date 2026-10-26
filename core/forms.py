from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile, Certificate

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        data = super().clean()
        if data.get("password") and data.get("confirm_password") and data["password"] != data["confirm_password"]:
            self.add_error("confirm_password", "Passwords do not match.")
        return data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["full_name", "education", "skills", "github_url", "linkedin_url"]
        widgets = {"skills": forms.Textarea(attrs={"rows": 3, "placeholder": "Python, SQL, Django, HTML"})}

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(help_text="Upload a PDF or DOCX file (max 5 MB).")

    def clean_resume(self):
        f = self.cleaned_data["resume"]
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File must be 5 MB or smaller.")
        if not f.name.lower().endswith((".pdf", ".docx", ".txt")):
            raise forms.ValidationError("Upload a PDF, DOCX, or TXT file.")
        return f

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["title", "issuer", "issue_date", "file"]
        widgets = {"issue_date": forms.DateInput(attrs={"type": "date"})}
