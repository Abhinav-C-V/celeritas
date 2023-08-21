from django import forms
from category.models import Category
from django.forms import ModelForm

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'offer_active', 'discount']
        widgets = {
            'category_name' : forms.TextInput(attrs={'class':'form-control'}),
            'offer_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels={
            'category_name':'Category Name',
            'offer_active': 'Offer Active',
            'discount': 'Discount Price',
        }