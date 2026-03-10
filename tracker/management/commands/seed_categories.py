"""
Seed default income and expense categories.
Run: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from tracker.models import Category


INCOME_CATEGORIES = [
    {'name': 'Salary', 'color': '#10B981', 'icon': 'briefcase'},
    {'name': 'Freelance', 'color': '#3B82F6', 'icon': 'laptop'},
    {'name': 'Business', 'color': '#8B5CF6', 'icon': 'trending-up'},
    {'name': 'Gift', 'color': '#EC4899', 'icon': 'gift'},
    {'name': 'Investment', 'color': '#F59E0B', 'icon': 'dollar-sign'},
    {'name': 'Other Income', 'color': '#14B8A6', 'icon': 'plus-circle'},
]

EXPENSE_CATEGORIES = [
    {'name': 'Food & Drinks', 'color': '#F97316', 'icon': 'utensils'},
    {'name': 'Transport', 'color': '#F59E0B', 'icon': 'car'},
    {'name': 'Rent/Housing', 'color': '#EF4444', 'icon': 'home'},
    {'name': 'Shopping', 'color': '#EC4899', 'icon': 'shopping-cart'},
    {'name': 'Utilities', 'color': '#3B82F6', 'icon': 'zap'},
    {'name': 'Health', 'color': '#10B981', 'icon': 'heart'},
    {'name': 'Entertainment', 'color': '#8B5CF6', 'icon': 'music'},
    {'name': 'Education', 'color': '#06B6D4', 'icon': 'book'},
    {'name': 'Data/Airtime', 'color': '#84CC16', 'icon': 'smartphone'},
    {'name': 'Other Expense', 'color': '#94a3b8', 'icon': 'tag'},
]


class Command(BaseCommand):
    help = 'Seed default categories'

    def handle(self, *args, **options):
        created = 0
        for item in INCOME_CATEGORIES:
            obj, was_created = Category.objects.get_or_create(
                name=item['name'], type='income',
                defaults={'color': item['color'], 'icon': item['icon']}
            )
            if was_created:
                created += 1

        for item in EXPENSE_CATEGORIES:
            obj, was_created = Category.objects.get_or_create(
                name=item['name'], type='expense',
                defaults={'color': item['color'], 'icon': item['icon']}
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created} default categories.'
        ))
