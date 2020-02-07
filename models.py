import secrets

from django.contrib.auth.models import User
from django.db import OperationalError, models

# Create your models here.

CATEGORIES = ((1, 'Trinken'), (2, 'Snacks'), (3, 'Eis'))


def generate_key():
    while True:
        key = secrets.token_hex(32)
        try:
            if not Purchase.objects.filter(key=key).exists():
                break
        except OperationalError:
            break

    return key


class Product(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    price = models.FloatField()
    category = models.IntegerField(choices=CATEGORIES)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    class Meta:
        ordering = ['-date']

    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, default=generate_key)

    def __str__(self):
        day = self.date.day
        month = self.date.month
        year = self.date.year
        hour = self.date.hour
        minute = self.date.minute
        second = self.date.second

        return '{} bought {} {} for €{:.2f} on {}.{}.{} at {}:{}:{}'.format(
            self.user,
            self.quantity,
            self.product.name,
            self.quantity * self.product.price,
            day,
            month,
            year,
            hour,
            minute,
            second
        )


class Deposit(models.Model):
    class Meta:
        ordering = ['-date']

    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} deposited €{:.2f} on {}'.format(self.user,
                                                   self.amount,
                                                   self.date.isoformat())


class Employee(models.Model):
    class Meta:
        ordering = ['user']

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)
    get_all_emails = models.BooleanField(default=True)

    def __str__(self):
        return self.user
