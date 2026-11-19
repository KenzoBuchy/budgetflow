# BudgetFlow

![tests](https://github.com/KenzoBuchy/budgetflow/actions/workflows/tests.yml/badge.svg)

Department budget tracking API built with Django, Django REST Framework and PostgreSQL.
Built as a learning project to move from FastAPI/SQLAlchemy to Django.

## Features
- Budgets per department and year, expenses by category
- REST API with Swagger docs (`/api/docs/`) and a reporting endpoint (`/api/budgets/summary/`)
- Role-based permissions (read-only controllers, budget owners) and object-level rules
- Audit trail: every expense records who created it
- Business validation: an expense must fall within its budget year
- Query optimisation: `select_related` and annotations, locked by a query-count test
- Tests with pytest, run on PostgreSQL in GitHub Actions

## Run it
    docker compose up --build -d
    docker compose exec web python manage.py createsuperuser
    docker compose exec web python manage.py seed_demo

Then open http://localhost:8000/api/docs/ or http://localhost:8000/admin/

## Tech choices
- `DecimalField` for all amounts (no floats for money)
- Business logic in a custom QuerySet (`Budget.objects.with_totals()`)
- Credentials in docker-compose are for local demo only