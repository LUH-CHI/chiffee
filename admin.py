from django.contrib import admin

# Register your models here.

from .models import Deposit, Employee, Product, Purchase


class DepositAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Deposit._meta.fields]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]


class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]


class PurchaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Purchase._meta.fields]


admin.site.register(Deposit, DepositAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
