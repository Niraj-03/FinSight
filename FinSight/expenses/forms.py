from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Groceries'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in ₹'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }