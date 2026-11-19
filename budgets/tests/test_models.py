from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from budgets.models import Budget, Expense


def test_totals_without_expense(budget):
    b = Budget.objects.with_totals().get(pk=budget.pk)
    assert b.spent == Decimal("0")
    assert b.remaining == Decimal("1000")


def test_totals_sum_expenses(budget, category):
    for amount in ("100.00", "250.50"):
        Expense.objects.create(budget=budget, category=category, label="x",
                               amount=Decimal(amount), spent_on=date(2026, 1, 10))
    b = Budget.objects.with_totals().get(pk=budget.pk)
    assert b.spent == Decimal("350.50")
    assert b.remaining == Decimal("649.50")


def test_one_budget_per_department_and_year(budget):
    with pytest.raises(IntegrityError):
        Budget.objects.create(department=budget.department, year=2026, amount=Decimal("1"))