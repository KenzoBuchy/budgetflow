from decimal import Decimal
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name}"

class BudgetQuerySet(models.QuerySet):
    def with_totals(self):
        return self.annotate(
            spent=Coalesce(
                Sum("expenses__amount"),
                Value(Decimal("0.00")),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            )
        ).annotate(remaining=F("amount") - F("spent"))

class Budget(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="budgets"
    )
    year = models.PositiveIntegerField()
    amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    objects = BudgetQuerySet.as_manager()

    class Meta:
        ordering = ["-year", "department__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "year"], name="unique_budget_per_department_year"
            )
        ]

    def __str__(self):
        return f"{self.department.code} {self.year}"

class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="expenses")
    label = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    spent_on = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on"]

    def __str__(self):
        return f"{self.label} ({self.amount})"