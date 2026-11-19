from decimal import Decimal

import pytest
from django.contrib.auth.models import Permission, User
from rest_framework.test import APIClient

from budgets.models import Budget, Category, Department


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def budget(db):
    dept = Department.objects.create(code="IT", name="Information Technology")
    return Budget.objects.create(department=dept, year=2026, amount=Decimal("1000.00"))


@pytest.fixture
def category(db):
    return Category.objects.create(name="Software")


@pytest.fixture
def make_user(db):
    def _make(username, *codenames):
        user = User.objects.create_user(username=username, password="pass1234")
        for codename in codenames:
            user.user_permissions.add(
                Permission.objects.get(codename=codename, content_type__app_label="budgets")
            )
        return user
    return _make


@pytest.fixture
def owner(make_user):
    return make_user("bob", "view_budget", "view_expense", "add_expense",
                     "change_expense", "delete_expense")


@pytest.fixture
def controller(make_user):
    return make_user("alice", "view_budget", "view_expense")