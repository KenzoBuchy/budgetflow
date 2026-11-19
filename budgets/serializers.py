from rest_framework import serializers

from .models import Budget, Category, Department, Expense


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "code", "name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class BudgetSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)          # read: nested object
    department_id = serializers.PrimaryKeyRelatedField(        # write: an id
        queryset=Department.objects.all(), source="department", write_only=True
    )
    spent = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = ["id", "department", "department_id", "year", "amount", "spent", "remaining"]


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = ["id", "budget", "category", "category_name", "label",
                  "amount", "spent_on", "created_by", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        budget = attrs.get("budget", getattr(self.instance, "budget", None))
        spent_on = attrs.get("spent_on", getattr(self.instance, "spent_on", None))
        if budget and spent_on and spent_on.year != budget.year:
            raise serializers.ValidationError(
                {"spent_on": "The expense date must be in the budget year."}
            )
        return attrs