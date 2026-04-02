import json
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense, Category, Budget
from .forms import ExpenseForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

# Import for Django REST Framework
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ExpenseSerializer

@login_required
def dashboard(request):
    today = datetime.date.today()
    
    # 1. Handle Form Submission (Adding Expenses & Receipts)
    if request.method == 'POST':
        # request.FILES is mandatory for receipt uploads
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    # 2. Fetch Data for the current user
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # 3. Calculate Monthly Summary
    monthly_total = expenses.filter(
        date__month=today.month, 
        date__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # 4. Fetch Budget
    budget = Budget.objects.filter(
        user=request.user, 
        month=today.month, 
        year=today.year
    ).first()

    # 5. Prepare Category Data for Chart.js
    category_sums = expenses.values('category__name').annotate(total=Sum('amount'))
    labels = [c['category__name'] for c in category_sums if c['category__name']]
    data = [float(c['total']) for c in category_sums if c['category__name']]

    context = {
        'expenses': expenses,
        'monthly_total': monthly_total,
        'budget': budget,
        'form': form,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'expenses/dashboard.html', context)

# API Endpoint as per Abstract Requirements
@api_view(['GET'])
def expense_api_list(request):
    expenses = Expense.objects.filter(user=request.user)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


# Add this register function
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})