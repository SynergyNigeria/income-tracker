from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'color', 'icon']
    list_filter = ['type']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'amount', 'category', 'description']
    list_filter = ['transaction_type', 'category', 'date']
    ordering = ['-date']
