from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Budget, Category, Department, Expense
from .serializers import (BudgetSerializer, CategorySerializer,
                          DepartmentSerializer, ExpenseSerializer)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return Budget.objects.with_totals().select_related("department")

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Reporting: consumption of each budget, plus totals."""
        budgets = self.filter_queryset(self.get_queryset())
        rows = [
            {
                "department": b.department.code,
                "year": b.year,
                "budget": b.amount,
                "spent": b.spent,
                "remaining": b.remaining,
                "consumption_rate": round(b.spent / b.amount * 100, 1) if b.amount else None,
            }
            for b in budgets
        ]
        return Response({
            "total_budget": sum(r["budget"] for r in rows),
            "total_spent": sum(r["spent"] for r in rows),
            "budgets": rows,
        })


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.select_related("budget__department", "category", "created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)   # audit trail, as in the admin