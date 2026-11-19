from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import Budget


class BudgetListView(ListView):
    """Class-based view (CBV)."""
    template_name = "budgets/budget_list.html"
    context_object_name = "budgets"

    def get_queryset(self):
        qs = Budget.objects.with_totals().select_related("department")
        year = self.request.GET.get("year")
        if year and year.isdigit():
            qs = qs.filter(year=int(year))
        return qs


def budget_detail(request, pk):
    """Function-based view (FBV), the closest to a FastAPI route."""
    budget = get_object_or_404(
        Budget.objects.with_totals().select_related("department"), pk=pk
    )
    expenses = budget.expenses.select_related("category").order_by("-spent_on")
    return render(request, "budgets/budget_detail.html",
                  {"budget": budget, "expenses": expenses})