import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from budgets.models import Budget, Category, Department, Expense

DEPARTMENTS = [("IT", "Information Technology"), ("RISK", "Risk Management"),
               ("FIN", "Finance"), ("HR", "Human Resources"), ("COMP", "Compliance")]
CATEGORIES = ["Software", "Hardware", "Travel", "Training", "Consulting"]


class Command(BaseCommand):
    help = "Fill the database with demo data"

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        Expense.objects.all().delete()
        Budget.objects.all().delete()
        Department.objects.all().delete()
        Category.objects.all().delete()

        depts = [Department.objects.create(code=c, name=n) for c, n in DEPARTMENTS]
        cats = [Category.objects.create(name=n) for n in CATEGORIES]

        for dept in depts:
            for year in (2025, 2026):
                budget = Budget.objects.create(
                    department=dept, year=year,
                    amount=Decimal(random.randrange(50_000, 300_000, 1_000)),
                )
                random_categ = random.choice(cats)
                Expense.objects.bulk_create([
                    Expense(
                        budget=budget,
                        category=random_categ,
                        label=f"{dept.code} expense {i + 1} in {random_categ.name}",
                        amount=Decimal(random.randrange(100, 8_000)),
                        spent_on=date(year, 1, 1) + timedelta(days=random.randrange(365)),
                    )
                    for i in range(25)
                ])
        self.stdout.write(self.style.SUCCESS("Demo data created: 10 budgets, 250 expenses"))