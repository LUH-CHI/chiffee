from django import forms
from .models import CATEGORIES

class ProductForm(forms.Form):
	product_active = forms.BooleanField(required=False)
	product_name = forms.CharField()
	product_price = forms.FloatField()
	product_categorie = forms.ChoiceField(choices=CATEGORIES)
