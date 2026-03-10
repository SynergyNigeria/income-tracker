from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.db.models import Sum
from datetime import date, timedelta
from django.utils import timezone as tz
from django.conf import settings as dj_settings
from .models import Category, Transaction, COLOR_CHOICES, ICON_CHOICES
import os


def pwa_sw(request):
    """Serve service worker at root scope /sw.js"""
    sw_path = os.path.join(dj_settings.BASE_DIR, 'static', 'sw.js')
    response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


def get_balance():
    total_income = Transaction.objects.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    return total_income - total_expense


def dashboard(request):
    total_income = Transaction.objects.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    today = date.today()
    month_start = today.replace(day=1)
    month_income = Transaction.objects.filter(
        transaction_type='income', date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    month_expense = Transaction.objects.filter(
        transaction_type='expense', date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    recent_transactions = Transaction.objects.select_related('category').all()[:8]
    categories = Category.objects.all()

    context = {
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'month_income': month_income,
        'month_expense': month_expense,
        'recent_transactions': recent_transactions,
        'categories': categories,
        'today': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'dashboard.html', context)


def _build_cumulative_balance(date_range_start):
    """Return balance running total up to (not including) date_range_start."""
    total = 0
    for t in Transaction.objects.filter(date__lt=date_range_start).order_by('date', 'created_at'):
        total += float(t.amount) if t.transaction_type == 'income' else -float(t.amount)
    return total


def api_chart_data(request):
    today = date.today()

    # ── Daily flow: last 30 days, last point = today ──────────────────────────
    daily_start = today - timedelta(days=29)
    running = _build_cumulative_balance(daily_start)
    daily_labels, daily_balance, daily_net = [], [], []
    for i in range(30):
        day = daily_start + timedelta(days=i)
        inc = Transaction.objects.filter(transaction_type='income',  date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Transaction.objects.filter(transaction_type='expense', date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        net = float(inc) - float(exp)
        running += net
        daily_labels.append(day.strftime('%b %d'))
        daily_balance.append(round(running, 2))
        daily_net.append(round(net, 2))

    # ── Weekly flow: last 12 weeks, last point = current week ─────────────────
    # Week starts Monday; current week end = last day of current week (Sun)
    week_offset = today.weekday()                         # 0=Mon … 6=Sun
    current_week_start = today - timedelta(days=week_offset)
    weekly_window_start = current_week_start - timedelta(weeks=11)
    running_w = _build_cumulative_balance(weekly_window_start)
    weekly_labels, weekly_balance, weekly_net = [], [], []
    for i in range(12):
        wk_start = weekly_window_start + timedelta(weeks=i)
        wk_end   = wk_start + timedelta(days=6)
        inc = Transaction.objects.filter(transaction_type='income',  date__gte=wk_start, date__lte=wk_end).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Transaction.objects.filter(transaction_type='expense', date__gte=wk_start, date__lte=wk_end).aggregate(Sum('amount'))['amount__sum'] or 0
        net = float(inc) - float(exp)
        running_w += net
        weekly_labels.append(wk_start.strftime('%b %d'))
        weekly_balance.append(round(running_w, 2))
        weekly_net.append(round(net, 2))

    # ── Monthly flow: last 12 months, last point = current month ──────────────
    monthly_flow_labels, monthly_flow_balance, monthly_flow_net = [], [], []
    monthly_flow_income, monthly_flow_expense = [], []
    first_of_12_months_ago_year = today.year
    first_of_12_months_ago_month = today.month - 11
    while first_of_12_months_ago_month <= 0:
        first_of_12_months_ago_month += 12
        first_of_12_months_ago_year -= 1
    monthly_window_start = date(first_of_12_months_ago_year, first_of_12_months_ago_month, 1)
    running_m = _build_cumulative_balance(monthly_window_start)
    for i in range(12):
        yr = first_of_12_months_ago_year
        mo = first_of_12_months_ago_month + i
        while mo > 12:
            mo -= 12
            yr += 1
        ms = date(yr, mo, 1)
        me = date(yr + 1, 1, 1) - timedelta(days=1) if mo == 12 else date(yr, mo + 1, 1) - timedelta(days=1)
        inc = Transaction.objects.filter(transaction_type='income',  date__gte=ms, date__lte=me).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Transaction.objects.filter(transaction_type='expense', date__gte=ms, date__lte=me).aggregate(Sum('amount'))['amount__sum'] or 0
        net = float(inc) - float(exp)
        running_m += net
        monthly_flow_labels.append(ms.strftime('%b %y'))
        monthly_flow_balance.append(round(running_m, 2))
        monthly_flow_net.append(round(net, 2))
        monthly_flow_income.append(float(inc))
        monthly_flow_expense.append(float(exp))

    # ── Hourly flow: last 24 hours (by created_at datetime) ───────────────────
    now_dt = tz.now()
    current_hour = now_dt.replace(minute=0, second=0, microsecond=0)
    hour_window_start = current_hour - timedelta(hours=23)
    running_h = 0.0
    for t in Transaction.objects.filter(created_at__lt=hour_window_start):
        running_h += float(t.amount) if t.transaction_type == 'income' else -float(t.amount)
    hourly_labels, hourly_balance, hourly_net = [], [], []
    hourly_inc_list, hourly_exp_list = [], []
    for i in range(24):
        slot_start = hour_window_start + timedelta(hours=i)
        slot_end   = slot_start + timedelta(hours=1)
        inc = Transaction.objects.filter(
            transaction_type='income',
            created_at__gte=slot_start, created_at__lt=slot_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Transaction.objects.filter(
            transaction_type='expense',
            created_at__gte=slot_start, created_at__lt=slot_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        net = float(inc) - float(exp)
        running_h += net
        h = slot_start.hour
        label = f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
        hourly_labels.append(label)
        hourly_balance.append(round(running_h, 2))
        hourly_net.append(round(net, 2))
        hourly_inc_list.append(float(inc))
        hourly_exp_list.append(float(exp))

    # ── Income sources breakdown (all time) ───────────────────────────────────
    income_source_labels, income_source_data, income_source_colors = [], [], []
    for cat in Category.objects.filter(type='income'):
        total = cat.transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        if total > 0:
            income_source_labels.append(cat.name)
            income_source_data.append(float(total))
            income_source_colors.append(cat.color)

    # ── Monthly spending by category (this month) ─────────────────────────────
    this_month_start = today.replace(day=1)
    cat_spend_labels, cat_spend_data, cat_spend_colors = [], [], []
    for cat in Category.objects.filter(type='expense'):
        total = cat.transactions.filter(transaction_type='expense', date__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
        if total > 0:
            cat_spend_labels.append(cat.name)
            cat_spend_data.append(float(total))
            cat_spend_colors.append(cat.color)

    return JsonResponse({
        'hourly_flow':  { 'labels': hourly_labels,       'balance': hourly_balance,       'net': hourly_net,
                          'income': hourly_inc_list, 'expense': hourly_exp_list },
        'daily_flow':   { 'labels': daily_labels,        'balance': daily_balance,        'net': daily_net },
        'weekly_flow':  { 'labels': weekly_labels,       'balance': weekly_balance,       'net': weekly_net },
        'monthly_flow': { 'labels': monthly_flow_labels, 'balance': monthly_flow_balance, 'net': monthly_flow_net,
                          'income': monthly_flow_income, 'expense': monthly_flow_expense },
        'income_sources':      { 'labels': income_source_labels, 'data': income_source_data, 'colors': income_source_colors },
        'monthly_category_spend': { 'labels': cat_spend_labels, 'data': cat_spend_data, 'colors': cat_spend_colors },
    })


# ── Transactions ─────────────────────────────────────────────────────────────

def transaction_list(request):
    transactions = Transaction.objects.select_related('category').all()
    t_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    month = request.GET.get('month', '')

    if t_type:
        transactions = transactions.filter(transaction_type=t_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if month:
        try:
            year, mon = month.split('-')
            transactions = transactions.filter(date__year=year, date__month=mon)
        except Exception:
            pass

    total_income = Transaction.objects.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'transactions': transactions,
        'categories': Category.objects.all(),
        'balance': total_income - total_expense,
        'filter_type': t_type,
        'filter_category': category_id,
        'filter_month': month,
    }
    return render(request, 'transactions/list.html', context)


def transaction_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('transaction_type')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '')
        trans_date = request.POST.get('date') or date.today()
        category = get_object_or_404(Category, id=category_id)
        Transaction.objects.create(
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            description=description,
            date=trans_date,
        )
        return redirect('dashboard')
    return render(request, 'transactions/form.html', {
        'categories': categories,
        'today': date.today().strftime('%Y-%m-%d'),
    })


def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        transaction.amount = request.POST.get('amount')
        transaction.transaction_type = request.POST.get('transaction_type')
        transaction.category = get_object_or_404(
            Category, id=request.POST.get('category')
        )
        transaction.description = request.POST.get('description', '')
        transaction.date = request.POST.get('date') or date.today()
        transaction.save()
        return redirect('transaction_list')
    return render(request, 'transactions/form.html', {
        'transaction': transaction,
        'categories': categories,
        'today': date.today().strftime('%Y-%m-%d'),
    })


def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {
        'item': transaction,
        'item_name': f'₦{transaction.amount} — {transaction.description or transaction.category.name}',
        'cancel_url': 'transaction_list',
    })


# ── Categories ────────────────────────────────────────────────────────────────

def category_list(request):
    income_categories = Category.objects.filter(type='income')
    expense_categories = Category.objects.filter(type='expense')
    return render(request, 'categories/list.html', {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    })


def category_add(request):
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            color=request.POST.get('color', '#10B981'),
            icon=request.POST.get('icon', 'tag'),
        )
        return redirect('category_list')
    return render(request, 'categories/form.html', {
        'color_choices': COLOR_CHOICES,
        'icon_choices': ICON_CHOICES,
    })


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.type = request.POST.get('type')
        category.color = request.POST.get('color', '#10B981')
        category.icon = request.POST.get('icon', 'tag')
        category.save()
        return redirect('category_list')
    return render(request, 'categories/form.html', {
        'category': category,
        'color_choices': COLOR_CHOICES,
        'icon_choices': ICON_CHOICES,
    })


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'transactions/confirm_delete.html', {
        'item': category,
        'item_name': category.name,
        'cancel_url': 'category_list',
    })
