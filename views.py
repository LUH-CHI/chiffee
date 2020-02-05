from itertools import chain

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from chiffee.filters import PurchaseFilter
from .models import CATEGORIES, Employee, Product, Purchase

EMAIL_ADDRESS = 'kaffeekasse@chi.uni-hannover.de'
EMAIL_SUBJECT = 'Kauf Kaffeekasse'

QUANTITY_RANGE = [1, 2, 3, 4, 5, 6]


def index(request):
    while True:
        if request.method != 'GET':
            break

        products = Product.objects.filter(
            active=True).order_by('category', 'name')

        context = {'categories': CATEGORIES, 'products': products}

        return render(request, 'chiffee/index.html', context)

    return render(request, 'chiffee/redirect.html')


def make_purchase(request, quantity=1):
    while True:
        if Group.objects.filter(name="professors").exists():
            groups = Group.objects.get(name="professors")
            professors = groups.user_set.all().filter(
                is_active=True).order_by('username')
        else:
            professors = Group.objects.none()

        if Group.objects.filter(name="employees").exists():
            groups = Group.objects.get(name="employees")
            employees = groups.user_set.all().filter(
                is_active=True).order_by('username')
        else:
            employees = Group.objects.none()

        if Group.objects.filter(name="students").exists():
            groups = Group.objects.get(name="students")
            students = groups.user_set.all().filter(
                is_active=True).order_by('username')
        else:
            students = Group.objects.none()

        users = list(chain(professors, employees, students))

        if request.method == 'GET':
            if 'product' not in request.GET:
                break

            products = Product.objects.filter(name=request.GET['product'])

            if not products.exists():
                break

            product = products[0]

            if 'quantity' in request.GET:
                try:
                    quantity = int(request.GET['quantity'])
                except ValueError:
                    break

                if quantity not in QUANTITY_RANGE:
                    break

            context = {'product': product,
                       'quantity': quantity,
                       'quantity_range': QUANTITY_RANGE,
                       'total_price': quantity * product.price,
                       'users': users}

            return render(request, 'chiffee/make_purchase.html', context)
        elif request.method == 'POST':
            if 'product' not in request.POST or 'quantity' not in request.POST:
                break

            products = Product.objects.filter(name=request.POST['product'])

            if not products.exists():
                break

            product = products[0]

            try:
                quantity = int(request.POST['quantity'])
            except ValueError:
                break

            if quantity not in QUANTITY_RANGE:
                break

            if request.user.is_authenticated:
                user = request.user
            else:
                users = User.objects.filter(username=request.POST['username'])

                if not users.exists():
                    break

                user = users[0]

            try:
                employee = user.employee
            except Employee.DoesNotExist:
                employee = Employee.objects.create(user=user)

            total_price = product.price * quantity
            employee.balance -= total_price
            employee.save()

            new_purchase = Purchase.objects.create(user=user,
                                                   product=product,
                                                   quantity=quantity,
                                                   total_price=total_price)

            url = request.get_raw_uri().replace(request.get_full_path(), '')
            url += reverse('chiffee:cancel-purchase',
                           kwargs={'key': new_purchase.key})

            if employee.get_all_emails:
                message = (f'Hallo {user.first_name} {user.last_name}!\n\n'
                           f'Sie haben {quantity} {product.name} '
                           f'für insgesamt €{total_price:.2f} gekauft.\n\n'
                           f'Ihr aktueller Kontostand beträgt '
                           f'€{employee.balance:.2f}.\n\n'
                           f'Wenn Sie diesen Kauf stornieren möchten, '
                           f'klicken Sie bitte hier: {url}')

                send_mail(EMAIL_SUBJECT,
                          message,
                          EMAIL_ADDRESS,
                          [user.email],
                          fail_silently=False)

            context = {'done': True}

            return render(request, 'chiffee/redirect.html', context)
        else:
            break

    return render(request, 'chiffee/redirect.html')


def cancel_purchase(request, key):
    context = {}

    while True:
        if request.method != 'GET':
            break

        purchases = Purchase.objects.filter(key=key)

        if not purchases.exists():
            break

        purchase = purchases[0]

        employee = purchase.user.employee
        employee.balance += purchase.total_price
        employee.save()

        if employee.get_all_emails:
            message = (f'Hallo {purchase.user.first_name} '
                       f'{purchase.user.last_name}!\n\n'
                       f'Sie haben Ihren Kauf von {purchase.quantity} '
                       f'{purchase.product.name} für insgesamt '
                       f'€{purchase.total_price:.2f} erfolgreich storniert.\n\n'
                       f'Ihr aktueller Kontostand beträgt '
                       f'€{employee.balance:.2f}.\n\n')

            send_mail(EMAIL_SUBJECT,
                      message,
                      EMAIL_ADDRESS,
                      [purchase.user.email],
                      fail_silently=False)

        purchase.delete()
        context['done'] = True
        break

    return render(request, 'chiffee/redirect.html', context)


@login_required
def view_my_purchases(request):
    if request.method == 'GET':

        purchases = Purchase.objects.filter(user=request.user)
        employees = Employee.objects.filter(user=request.user)

        if not employees.exists():
            employee = Employee.objects.create(user=request.user)
        else:
            employee = employees[0]

        context = {'purchases': purchases, 'balance': employee.balance}

        return render(request, 'chiffee/my_purchases.html', context)

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def view_all_purchases(request):
    if request.method == 'GET':
        purchase_filter = PurchaseFilter(request.GET)
        all_products = Product.objects.all()
        purchases = {}
        total_counter = 0

        for product in all_products:
            counter = 0

            for purchase in purchase_filter.qs:
                if purchase.product.name == product.name:
                    counter += 1

            purchases[product.name] = counter
            total_counter += counter

        context = {'filter': purchase_filter,
                   'purchases': purchases,
                   'total_counter': total_counter}

        return render(request, 'chiffee/all_purchases.html', context)

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def accounts(request):
    while True:
        context = {'users': User.objects.order_by('last_name', 'first_name')}

        if request.method == 'GET':
            if 'username' in request.GET:
                context['username'] = request.GET['username']

            return render(request, 'chiffee/accounts.html', context)
        elif request.method == 'POST':
            if 'username' not in request.POST or 'balance' not in request.POST:
                break

            users = User.objects.filter(username=request.POST['username'])

            if not users.exists():
                break

            user = users[0]
            employees = Employee.objects.filter(user=user)

            if not employees.exists():
                user.employee = Employee.objects.create(user=user)

            user.employee.balance = request.POST['balance']

            try:
                user.employee.save()
            except ValueError:
                break

            return render(request, 'chiffee/accounts.html', context)
        else:
            break

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def products(request):
    while True:
        active_products = Product.objects.filter(
            active=True).order_by('category', 'name')
        inactive_products = Product.objects.filter(active=False)

        context = {'categories': CATEGORIES,
                   'active_products': active_products,
                   'inactive_products': inactive_products}

        if request.method == 'GET':
            if 'product' in request.GET:
                context['product'] = request.GET['product']

            return render(request, 'chiffee/products.html', context)
        elif request.method == 'POST':
            if all(param in request.POST
                   for param in ['product', 'price', 'category']):

                edit_products = Product.objects.filter(
                    name=request.POST['product'])

                if not edit_products.exists():
                    break

                product = edit_products[0]
                product.price = request.POST['price']

                for category in CATEGORIES:
                    if request.POST['category'] == category[1]:
                        product.category = category[0]
                        break

                if 'active' in request.POST and request.POST['active'] == 'on':
                    product.active = True
                else:
                    product.active = False

                try:
                    product.save()
                except ValueError:
                    break
            elif 'product' in request.POST:
                edit_products = Product.objects.filter(
                    name=request.POST['product'])

                if not edit_products.exists():
                    break

                product = edit_products[0]

                if not product.active:
                    product.active = True
                    product.save()

            return render(request, 'chiffee/products.html', context)
        else:
            break

    return render(request, 'chiffee/redirect.html')
