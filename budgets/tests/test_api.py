from datetime import date
from decimal import Decimal

import pytest

from budgets.models import Expense

pytestmark = pytest.mark.django_db


def payload(budget, category, **overrides):
    data = {"budget": budget.id, "category": category.id, "label": "IDE licences",
            "amount": "120.00", "spent_on": "2026-02-01"}
    return {**data, **overrides}


def test_anonymous_is_rejected(api):
    response = api.get("/api/expenses/")
    # 403 because SessionAuthentication is the first auth class (401 if Token came first)
    assert response.status_code in (401, 403)


def test_owner_creates_expense_with_audit_trail(api, owner, budget, category):
    api.force_authenticate(owner)
    response = api.post("/api/expenses/", payload(budget, category), format="json")
    assert response.status_code == 201
    assert Expense.objects.get().created_by == owner


def test_expense_outside_budget_year_is_refused(api, owner, budget, category):
    api.force_authenticate(owner)
    response = api.post("/api/expenses/", payload(budget, category, spent_on="2025-12-31"),
                        format="json")
    assert response.status_code == 400
    assert "spent_on" in response.data


def test_controller_is_read_only(api, controller, budget, category):
    api.force_authenticate(controller)
    assert api.get("/api/expenses/").status_code == 200
    assert api.post("/api/expenses/", payload(budget, category), format="json").status_code == 403


def test_cannot_delete_someone_elses_expense(api, make_user, owner, budget, category):
    expense = Expense.objects.create(budget=budget, category=category, label="x",
                                     amount=Decimal("10"), spent_on=date(2026, 1, 1),
                                     created_by=owner)
    other = make_user("carol", "view_expense", "delete_expense")
    api.force_authenticate(other)
    assert api.delete(f"/api/expenses/{expense.id}/").status_code == 403


def test_summary_consumption_rate(api, controller, budget, category):
    Expense.objects.create(budget=budget, category=category, label="x",
                           amount=Decimal("250"), spent_on=date(2026, 5, 1))
    api.force_authenticate(controller)
    response = api.get("/api/budgets/summary/?year=2026")
    assert response.status_code == 200
    assert response.data["budgets"][0]["consumption_rate"] == 25


def test_expense_list_has_no_n_plus_one(api, controller, budget, category,
                                        django_assert_max_num_queries):
    Expense.objects.bulk_create([
        Expense(budget=budget, category=category, label=f"e{i}",
                amount=Decimal("10"), spent_on=date(2026, 1, 1))
        for i in range(15)
    ])
    api.force_authenticate(controller)
    with django_assert_max_num_queries(5):   # count + list + permissions, whatever the number of rows
        response = api.get("/api/expenses/")
    assert response.status_code == 200