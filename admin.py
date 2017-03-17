from django.contrib import admin

# Register your models here.


from .models import Product, Buy, Employee

admin.site.register((Product, Buy, Employee))
