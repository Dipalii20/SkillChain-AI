from django.core.management.base import BaseCommand
from core.models import Internship

SAMPLE = [
    ("Python Web Development Intern", "CodeNest Labs", "Remote",
     "Build Django features and work with REST endpoints.",
     "python, django, sql, html, css, git"),
    ("Java Developer Intern", "ByteBridge", "Mumbai / Hybrid",
     "Assist with Java backend development and database tasks.",
     "java, sql, git, problem solving, rest api"),
    ("Junior Data Analyst Intern", "InsightWorks", "Remote",
     "Clean datasets and prepare reports for product teams.",
     "python, sql, excel, pandas, data analysis"),
    ("Machine Learning Intern", "ModelSpring", "Pune / Hybrid",
     "Prepare text datasets and evaluate baseline ML models.",
     "python, machine learning, scikit-learn, pandas, sql"),
    ("Web3 Developer Intern", "ChainCraft", "Remote",
     "Learn Solidity contracts and interact with EVM networks.",
     "solidity, blockchain, web3.py, javascript, git"),
    ("Frontend Developer Intern", "PixelStack", "Mumbai",
     "Create responsive pages and improve usability.",
     "html, css, javascript, bootstrap, git"),
]

class Command(BaseCommand):
    help = "Add sample internship listings for local demonstration."

    def handle(self, *args, **options):
        for title, company, location, description, skills in SAMPLE:
            Internship.objects.update_or_create(
                title=title, company=company,
                defaults={"location": location, "description": description,
                          "required_skills": skills, "is_active": True}
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(SAMPLE)} sample internships."))
