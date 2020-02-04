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

QUANTITY_RANGE = range(1, 6)


def index(request):
    if request.method == 'GET':
        products = Product.objects.order_by('category', 'name')
        active_products = []

        for product in products:
            if product.active:
                active_products.append(product)

        context = {'categories': CATEGORIES,
                   'active_products': active_products}

        return render(request, 'chiffee/index.html', context)

    return render(request, 'chiffee/redirect.html')


def make_purchases(request, quantity=1):
    while True:
        if request.method == 'POST' and 'product-name' in request.POST:
            products = Product.objects.filter(name=request.POST['product-name'])

            if products.exists():
                product = products[0]

                if 'quantity' in request.POST:
                    try:
                        new_quantity = int(request.POST['quantity'])
                    except ValueError:
                        break

                    if new_quantity not in QUANTITY_RANGE:
                        break

                    quantity = new_quantity

                if Group.objects.filter(name="professors").exists():
                    groups = Group.objects.get(name="professors")
                    professors = groups.user_set.all().order_by('username')
                else:
                    professors = Group.objects.none()

                if Group.objects.filter(name="employees").exists():
                    groups = Group.objects.get(name="employees")
                    employees = groups.user_set.all().order_by('username')
                else:
                    employees = Group.objects.none()

                if Group.objects.filter(name="students").exists():
                    groups = Group.objects.get(name="students")
                    students = groups.user_set.all().order_by('username')
                else:
                    students = Group.objects.none()

                users = list(chain(professors, employees, students))
                context = {'product': product,
                           'quantity': quantity,
                           'quantity_range': QUANTITY_RANGE,
                           'total_price': quantity * product.price,
                           'users': users}

                return render(request, 'chiffee/make_purchase.html', context)

        break

    return render(request, 'chiffee/redirect.html')


def confirm_purchases(request):
    while True:
        if (request.method == 'POST'
                and 'confirm' in request.POST
                and 'name' in request.POST
                and 'quantity' in request.POST):
            products = Product.objects.filter(name=request.POST['name'])

            if products.exists():
                product = products[0]

                try:
                    quantity = int(request.POST['quantity'])
                except ValueError:
                    break

                if quantity not in QUANTITY_RANGE:
                    break

                user = None

                if request.user.is_authenticated:
                    user = request.user
                else:
                    users = User.objects.filter(
                        username=request.POST['confirm'])

                    if users.exists():
                        user = users[0]

                if user is not None:
                    try:
                        employee = user.employee
                    except Employee.DoesNotExist:
                        employee = Employee.objects.create(user=user)

                    total_price = product.price * quantity
                    employee.balance -= total_price
                    employee.save()

                    new_purchase = Purchase.objects.create(
                        user=user,
                        product=product,
                        quantity=quantity,
                        total_price=total_price)
                    url = request.get_raw_uri().replace(
                        request.get_full_path(), '')
                    url += reverse('chiffee:cancel-purchases',
                                   kwargs={'key': new_purchase.key})

                    if employee.get_all_emails:
                        message = ('Hallo {} {}.\n\n'
                                   'Sie haben {} {} '
                                   'für insgesamt €{:.2f} gekauft.\n\n'
                                   'Dein Guthaben ist jetzt €{:.2f}.\n\n'
                                   'Wenn Sie diesen Kauf nicht getätigt haben, '
                                   'klicken Sie hier: {}')
                        message = message.format(user.first_name,
                                                 user.last_name,
                                                 quantity,
                                                 product.name,
                                                 total_price,
                                                 employee.balance,
                                                 url)

                        send_mail(EMAIL_SUBJECT,
                                  message,
                                  EMAIL_ADDRESS,
                                  [user.email],
                                  fail_silently=False)

                    context = {'done': True}

                    return render(request, 'chiffee/redirect.html', context)

        break

    return render(request, 'chiffee/redirect.html')


def cancel_purchases(request, key):
    context = {}

    if request.method == 'GET':
        purchases = Purchase.objects.filter(key=key)

        if purchases.exists():
            purchase = purchases[0]

            employee = purchase.user.employee
            employee.balance += purchase.total_price
            employee.save()

            purchase.delete()
            context['done'] = True

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
def view_accounts(request, edit_username=None):
    context = {'users': User.objects.order_by('last_name', 'first_name')}

    if request.method == 'GET':
        return render(request, 'chiffee/accounts.html', context)
    elif request.method == 'POST':
        if edit_username is not None:
            context['edit_username'] = edit_username

        return render(request, 'chiffee/accounts.html', context)

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def edit_accounts(request):
    while True:
        if request.method == 'POST' and 'edit' in request.POST:
            users = User.objects.filter(username=request.POST['edit'])

            if users.exists():
                return view_accounts(request, users[0].username)
        elif (request.method == 'POST'
              and 'confirm' in request.POST
              and 'balance' in request.POST):
            users = User.objects.filter(username=request.POST['confirm'])

            if users.exists():
                user = users[0]
                user.employee.balance = request.POST['balance']

                try:
                    user.employee.save()
                except ValueError:
                    break

                return redirect('chiffee:view-accounts')

        break

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def view_products(request, edit_name=None):
    active_products = Product.objects.filter(
        active=True).order_by('category', 'name')
    inactive_products = Product.objects.filter(active=False)

    context = {'categories': CATEGORIES,
               'active_products': active_products,
               'inactive_products': inactive_products}

    if request.method == 'GET':
        return render(request, 'chiffee/products.html', context)
    elif request.method == 'POST':
        if edit_name is not None:
            context['edit_name'] = edit_name

        return render(request, 'chiffee/products.html', context)

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def edit_products(request):
    while True:
        if request.method == 'POST' and 'edit' in request.POST:
            products = Product.objects.filter(name=request.POST['name'])

            if products.exists():
                return view_products(request, products[0].name)
        elif (request.method == 'POST'
              and 'confirm' in request.POST
              and 'name' in request.POST
              and 'price' in request.POST
              and 'category' in request.POST):
            products = Product.objects.filter(name=request.POST['confirm'])

            if products.exists():
                product = products[0]
                product.name = request.POST['name']

                try:
                    product.save()
                except ValueError:
                    break

                product.price = request.POST['price']

                try:
                    product.save()
                except ValueError:
                    break

                for category in CATEGORIES:
                    if request.POST['category'] == category[1]:
                        product.category = category[0]
                        break

                if 'active' in request.POST and request.POST['active'] == 'on':
                    product.active = True
                else:
                    product.active = False

                product.save()

                return redirect('chiffee:view-products')

        break

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def restore_products(request):
    if request.method == 'POST' and 'restore' in request.POST:
        products = Product.objects.filter(name=request.POST['name'])

        if products.exists():
            product = products[0]
            product.active = True
            product.save()

            return redirect('chiffee:view-products')

    return render(request, 'chiffee/redirect.html')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def view_all_purchases(request):
    if request.method == 'GET':
        purchase_filter = PurchaseFilter(request.GET)
        products = Product.objects.all()
        purchases = {}
        total_counter = 0

        for product in products:
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
