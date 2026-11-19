from decimal import Decimal
from django.contrib import admin
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from .models import Budget, Category, Department, Expense


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["code", "name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    fields = ["label", "category", "amount", "spent_on"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["department", "year", "amount", "total_spent", "remaining"]
    list_filter = ["year", "department"]
    list_select_related = ["department"]   # évite le N+1 sur la colonne department
    inlines = [ExpenseInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _total_spent=Coalesce(
                Sum("expenses__amount"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        ).annotate(_remaining=F("amount") - F("_total_spent"))

    @admin.display(description="Spent", ordering="_total_spent")
    def total_spent(self, obj):
        return obj._total_spent

    @admin.display(description="Remaining", ordering="_remaining")
    def remaining(self, obj):
        return obj._remaining


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["label", "budget", "category", "amount", "spent_on", "created_by"]
    list_filter = ["category", "budget__year", "budget__department"]
    search_fields = ["label"]
    date_hierarchy = "spent_on"
    list_select_related = ["budget__department", "category", "created_by"]
    autocomplete_fields = ["category"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)