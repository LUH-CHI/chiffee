from django.db import models

# Create your models here.
from django.contrib.auth.models import User

CATEGORIES = (
		('D', 'Trinken'),
		('F', 'Snacks'),
		('I', 'Eis'),
	)

class Product(models.Model):
	product_name = models.CharField(max_length=200)
	product_price = models.FloatField()
	product_categorie = models.CharField(max_length=1, choices=CATEGORIES, default="D")
	product_active = models.BooleanField(default=True)

	def __str__(self):              # __unicode__ on Python 2
		return (str(self.product_name) + " (" + str(self.product_price) + ")")

class Buy(models.Model):
	buy_date = models.DateTimeField(auto_now_add=True)
	buy_count = models.IntegerField()
	buy_product = models.ForeignKey(Product, on_delete=models.PROTECT) # it is not possible to delete a 'Product'
	buy_user = models.ForeignKey(User, default=None, on_delete=models.CASCADE) # if the user is deleted, delete this 'Buy' too.
	buy_total = models.FloatField(default=0.0)
	buy_address = models.CharField(max_length=20, default="keine")

	def __str__(self):              # __unicode__ on Python 2
		return (str(self.buy_user) + " bought " + str(self.buy_count) + " "  + str(self.buy_product))

class Deposit(models.Model):
	deposit_date = models.DateTimeField(auto_now_add=True)
	deposit_value = models.FloatField(default=0.0)
	deposit_user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

	def __str__(self):              # __unicode__ on Python 2
		return (str(self.deposit_user) + " (" + str(self.deposit_value) + ")")


class Employee(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.FloatField(default=0.0)
	allMails = models.BooleanField(default=True)

	def __str__(self):              # __unicode__ on Python 2
		return (str(self.user) + " (" + str(self.balance) + ")")
