from django import forms

from .models import CATEGORIES


class ProductForm(forms.Form):
    name = forms.CharField()
    category = forms.ChoiceField(choices=CATEGORIES)
    price = forms.FloatField()
    active = forms.BooleanField(required=False)
