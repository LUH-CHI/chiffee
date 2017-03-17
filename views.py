#!/usr/bin/env python
# encoding=utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from pprint import pprint

from .models import Product, Buy, CATEGORIES, Employee


fromaddr = "kaffeekasse@chi.uni-hannover.de"
subject  = "Kauf Kaffeekasse"

@login_required(login_url='chiffee:login')
def showhistory(request):
	context = {}
	context['user'] = request.user.first_name + " " + request.user.last_name
	try:
		u2 = request.user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=request.user)
		u2.save()
	context['balance'] = u2.balance
	try:
		context['buys'] = Buy.objects.filter(buy_user=request.user)
	except Buy.DoesNotExist:
		context['error'] = "Du hast bis jetzt noch nichts gekauft."
	return render(request, 'chiffee/history.html', context)

def products(request):
	context = {}
	context['categories'] = CATEGORIES
	context['products'] = Product.objects.order_by('product_categorie')
	return render(request, 'chiffee/products.html', context)

def users(request,productID):
	get_object_or_404(Product, product_name=productID)
	context = {}
	context['product'] = productID
	context['users'] = User.objects.all()
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

