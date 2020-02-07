import django_filters
from django import forms
from django.contrib.auth.models import User

from chiffee.models import Product, Purchase


class PurchaseFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    product = django_filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    date = django_filters.DateRangeFilter(
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Purchase
        fields = ['user', 'product', 'date']
