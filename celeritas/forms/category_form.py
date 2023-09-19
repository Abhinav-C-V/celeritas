from django import forms
from category.models import Category
from django.forms import ModelForm
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'offer_active', 'discount']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'offer_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'category_name': 'Category Name',
            'offer_active': 'Offer Active',
            'discount': 'Discount Price',
        }

    def clean(self):
        cleaned_data = super().clean()
        offer_active = self.cleaned_data['offer_active']
        discount = self.cleaned_data['discount']

        # Check if offer_active is True and discount is None or 0
        if offer_active and (discount is None or discount <= 0):
            raise forms.ValidationError("A discount greater than 0 is required.")

        return cleaned_data



