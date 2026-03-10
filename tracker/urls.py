from django.urls import path
from . import views

urlpatterns = [
    # PWA
    path('sw.js', views.pwa_sw, name='pwa_sw'),
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # API
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
