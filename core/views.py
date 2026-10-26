from pathlib import Path
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .ai_utils import extract_skills, match_score
from .blockchain import file_sha256, make_demo_record
from .forms import RegisterForm, ProfileForm, ResumeUploadForm, CertificateForm
from .models import StudentProfile, Internship, ResumeAnalysis, Certificate

def home(request):
    internships = Internship.objects.filter(is_active=True)[:3]
    return render(request, "core/home.html", {"internships": internships})

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        StudentProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Account created. Complete your profile to get better matches.")
        return redirect("profile")
    return render(request, "core/form_page.html", {"form": form, "heading": "Create your account", "button": "Register"})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Invalid username or password."
    return render(request, "core/login.html", {"error": error})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home")


def get_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile

@login_required
def dashboard(request):
    profile = get_profile(request.user)
    skill_list = profile.skill_list()
    matches = []
    for internship in Internship.objects.filter(is_active=True):
        score, matched, missing = match_score(skill_list, internship.required_skills)
        matches.append({"internship": internship, "score": score, "matched": matched, "missing": missing})
    matches.sort(key=lambda item: item["score"], reverse=True)
    return render(request, "core/dashboard.html", {
        "profile": profile,
        "matches": matches[:6],
        "analysis_count": ResumeAnalysis.objects.filter(user=request.user).count(),
        "certificate_count": Certificate.objects.filter(user=request.user).count(),
    })

@login_required
def profile(request):
    instance = get_profile(request.user)
    form = ProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("dashboard")
    return render(request, "core/form_page.html", {"form": form, "heading": "Your student profile", "button": "Save profile"})

def read_resume(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        import fitz
        doc = fitz.open(stream=uploaded.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if name.endswith(".docx"):
        from docx import Document
        import io
        doc = Document(io.BytesIO(uploaded.read()))
        return "\n".join(p.text for p in doc.paragraphs)
    return uploaded.read().decode("utf-8", errors="ignore")

@login_required
def analyze_resume(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)
    result = None
    if request.method == "POST" and form.is_valid():
        uploaded = form.cleaned_data["resume"]
        try:
            text = read_resume(uploaded)
            skills = extract_skills(text)
            analysis = ResumeAnalysis.objects.create(
                user=request.user,
                filename=uploaded.name,
                extracted_skills=", ".join(skills),
                extracted_text_preview=text[:1200],
            )
            profile = get_profile(request.user)
            merged = sorted(set(profile.skill_list()) | set(skills))
            profile.skills = ", ".join(merged)
            profile.save(update_fields=["skills"])
            result = {"skills": skills, "filename": uploaded.name, "analysis": analysis}
            messages.success(request, "Resume analyzed. Review your extracted skills in your profile.")
        except Exception as exc:
            messages.error(request, f"Could not read this file: {exc}")
    return render(request, "core/analyze_resume.html", {"form": form, "result": result})

def internships(request):
    profile = get_profile(request.user) if request.user.is_authenticated else None
    skills = profile.skill_list() if profile else []
    items = []
    for internship in Internship.objects.filter(is_active=True):
        score, matched, missing = match_score(skills, internship.required_skills)
        items.append({"internship": internship, "score": score, "matched": matched, "missing": missing})
    items.sort(key=lambda item: item["score"], reverse=True)
    return render(request, "core/internships.html", {"items": items, "has_profile": bool(profile)})

@login_required
def certificates(request):
    form = CertificateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cert = form.save(commit=False)
        cert.user = request.user
        uploaded = form.cleaned_data.get("file")
        if uploaded:
            cert.sha256_hash = file_sha256(uploaded)
        else:
            # No file means hash the certificate metadata; label it clearly in the UI.
            from .blockchain import text_sha256
            cert.sha256_hash = text_sha256(f"{cert.title}|{cert.issuer}|{cert.issue_date or ''}|{request.user.pk}")
        cert.save()
        make_demo_record(cert)
        messages.success(request, "Certificate fingerprint registered in local demo mode.")
        return redirect("certificates")
    records = Certificate.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "core/certificates.html", {"form": form, "records": records})

@login_required
def verify_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, pk=certificate_id, user=request.user)
    uploaded = request.FILES.get("verification_file")
    result = None
    if request.method == "POST":
        if uploaded:
            submitted_hash = file_sha256(uploaded)
            result = {"match": submitted_hash == cert.sha256_hash, "submitted_hash": submitted_hash}
        else:
            result = {"match": False, "error": "Choose a file to compare with the registered certificate."}
    return render(request, "core/verify_certificate.html", {"certificate": cert, "result": result})

def public_verify(request):
    record_id = request.GET.get("record_id", "").strip()
    cert = None
    if record_id:
        cert = Certificate.objects.filter(chain_record_id=record_id, is_registered=True).first()
    return render(request, "core/public_verify.html", {"record_id": record_id, "certificate": cert})
