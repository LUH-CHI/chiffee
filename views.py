#!/usr/bin/env python
# encoding=utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

from pprint import pprint

from .models import Product, Buy, CATEGORIES, Employee, Deposit


fromaddr = "kaffeekasse@chi.uni-hannover.de"
subject  = "Kauf Kaffeekasse"

@login_required(login_url='chiffee:login')
def showhistory(request):
	context = {}
	context['users'] = User.objects.all()
	try:
		context['buys'] = Buy.objects.filter(buy_user=request.user)
	except Buy.DoesNotExist:
		pass
	try:
		u2 = request.user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=request.user)
		u2.save()
	context['balance'] = u2.balance
	return render(request, 'chiffee/history.html', context)

@login_required(login_url='chiffee:login')
def showoverview(request):
	context = {}
	context['users'] = User.objects.all()

	if "POST" == request.method and "neu1" in request._post.keys():
		user = authenticate(username=request.user.username, password=request._post["old"])
		if user is not None:
			# A backend authenticated the cred
			if request._post["neu1"] == request._post["neu2"]:
				user.set_password(request._post["neu1"])
				user.save()
				context["error"] = "Passwort geändert"
			else:
				context["error"] = "Die neuen Passwörter stimmen nicht überein!"
		else:
			# No backend authenticated the credentials
			context['error'] = "Passwort nicht korrekt!"

	if request.user.is_superuser and "POST" == request.method and "nutzer" in request._post.keys():
		try:
			profiteer = User.objects.get(username=request._post["nutzer"])
			money = float(request._post["value"])
			d = Deposit(deposit_user = profiteer, deposit_value = money)
			d.save()
			try:
				u2 = profiteer.employee
			except Employee.DoesNotExist:
				u2 = Employee(user=profiteer)
			u2.balance = u2.balance + money
			u2.save()
			context['payment'] = d
			msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromaddr,profiteer.email,"Gutschrift Kaffeekasse"))
			msg = ("Hallo %s %s.\n\r\n\r" % (profiteer.first_name, profiteer.last_name))
			msg = msg + ("Du hast soeben %0.2f Euro gut geschrieben bekommen.\n\r" % (money))
			msg = msg + ("Aktueller Kontostand: %7.2f Euro.\n\r\n\r" % (u2.balance))
			msg = msg + ("Es dankt,\n\rKarlo Kaffeekasse\n\r")
			email = EmailMessage("Gutschrift Kaffeekasse", msg, fromaddr, [profiteer.email])
			email.send()
		except:
			context['error'] = "Irgendwas lief schief beim einzahlen"
	try:
		u2 = request.user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=request.user)
		u2.save()
	context['balance'] = u2.balance
	return render(request, 'chiffee/overview.html', context)

@login_required(login_url='chiffee:login')
def showmoney(request):
	context = {}
	context['users'] = []
	if request.user.is_superuser:
		for u in User.objects.order_by('last_name', 'first_name'):
			try:
				u2 = {};
				u2['first_name'] = u.first_name
				u2['last_name'] = u.last_name
				u2['balance'] = u.employee.balance
				if u.employee.balance != 0:
					context['users'].append(u2)
			except:
				pass
	return render(request, 'chiffee/money.html', context)

@login_required(login_url='chiffee:login')
@user_passes_test(lambda u: u.is_superuser)
def showproducts(request):
	context = {}
	context['categories'] = CATEGORIES
	context['products'] = Product.objects.order_by('product_categorie')
	return render(request, 'chiffee/productoverview.html', context)

def products(request):
	context = {}
	context['categories'] = CATEGORIES
	context['products'] = Product.objects.order_by('product_categorie')
	return render(request, 'chiffee/products.html', context)

def users(request,productID):
	get_object_or_404(Product, product_name=productID)
	context = {}
	context['product'] = productID
	context['profs'] = Group.objects.get(name="prof").user_set.all().order_by('username')
	context['wimi'] = Group.objects.get(name="wimi").user_set.all().order_by('username')
	context['stud'] = Group.objects.get(name="stud").user_set.all().order_by('username')
	return render(request, 'chiffee/user.html', context)

def confirm(request,productID, userID):
	get_object_or_404(Product, product_name=productID)
	user = get_object_or_404(User, username=userID)
	context = {}
	context['product'] = productID
	context['user'] = userID
	context['username'] = user.first_name + " " + user.last_name
	return render(request, 'chiffee/confirm.html', context)

def confirmed(request,productID, userID,count):
	product = get_object_or_404(Product, product_name=productID)
	user = get_object_or_404(User, username=userID)
	context = {}
	b = Buy(buy_count = count, buy_product = product, buy_user = user, buy_address=request.environ['REMOTE_ADDR'], buy_total=(product.product_price * int(count)))
	b.save()
	try:
		u2 = user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=user)
		u2.save()
	u2.balance = u2.balance - (product.product_price * int(count))
	u2.save()
	if u2.allMails:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromaddr,user.email,subject))
		msg = ("Hallo %s %s.\n\r\n\r" % (user.first_name, user.last_name))
		msg = msg + ("Du hast soeben %d %s zu je %0.2f Euro gekauft.\n\r" % (int(count), product.product_name, product.product_price))
		msg = msg + ("Das macht insgesamt:  %7.2f Euro.\n\r" % (product.product_price * int(count)))
		msg = msg + ("Aktueller Kontostand: %7.2f Euro.\n\r\n\r" % (u2.balance))
		msg = msg + ("Es dankt,\n\rKarlo Kaffeekasse\n\r")
		email = EmailMessage(subject, msg, fromaddr, [user.email])
		email.send()
	return render(request, 'chiffee/confirmed.html', context)

