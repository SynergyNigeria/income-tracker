from django.db import models
from django.utils import timezone


ICON_CHOICES = [
    ('briefcase', 'Briefcase'),
    ('trending-up', 'Trending Up'),
    ('gift', 'Gift'),
    ('dollar-sign', 'Dollar Sign'),
    ('credit-card', 'Credit Card'),
    ('shopping-cart', 'Shopping Cart'),
    ('utensils', 'Utensils'),
    ('home', 'Home'),
    ('car', 'Car'),
    ('zap', 'Zap'),
    ('heart', 'Heart'),
    ('tag', 'Tag'),
    ('smartphone', 'Smartphone'),
    ('music', 'Music'),
    ('book', 'Book'),
    ('coffee', 'Coffee'),
]

COLOR_CHOICES = [
    ('#10B981', 'Emerald'),
    ('#3B82F6', 'Blue'),
    ('#F59E0B', 'Amber'),
    ('#EF4444', 'Red'),
    ('#8B5CF6', 'Purple'),
    ('#EC4899', 'Pink'),
    ('#14B8A6', 'Teal'),
    ('#F97316', 'Orange'),
    ('#06B6D4', 'Cyan'),
    ('#84CC16', 'Lime'),
]


class Category(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    color = models.CharField(max_length=7, default='#10B981')
    icon = models.CharField(max_length=50, default='tag')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='transactions'
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: ₦{self.amount} on {self.date}"

    class Meta:
        ordering = ['-date', '-created_at']
