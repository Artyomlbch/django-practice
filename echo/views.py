import datetime
import json
from logging import exception

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Books, User, Orders
from django.template import loader
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomCreationForm, LoginForm
from .decorators import unauthenticated_user, allowed_users, superuser_allowed_only
from .cart import Cart
from django.core.cache import cache
from django.views.decorators.cache import never_cache




# Create your views here.
def homePageView(request):
    request.session['filtered_books'] = False
    template = loader.get_template("index.html")
    if request.user:
        username = request.user.username
        context = {'username': username}
    else:
        context = {}
    return HttpResponse(template.render(context, request))


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            group = Group.objects.get(name='user')
            user.groups.add(group)

            login(request, user)

            return redirect('home')
    else:
        form = CustomCreationForm()

    return render(request, 'register.html', {'form': form})


def validate_username(request):
    username = request.GET.get("username", None)
    response = {
        'is_taken': User.objects.filter(username=username).exists()
    }

    return JsonResponse(response)


def validate_email(request):
    email = request.GET.get("email", None)
    if '@' not in email and '.' not in email:
        response = {
            'is_taken': True
        }
    else:
        response = {
            'is_taken': User.objects.filter(email=email).exists()
        }

    return JsonResponse(response)


def validate_password(request):
    response = {
        'allowed': len(request.GET.get("password", None)) >= 8,
    }

    return JsonResponse(response)


@unauthenticated_user
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)

                    return redirect(request.GET.get('next', 'home'))
                else:
                    return HttpResponse('Disabled account!')
            else:
                messages.add_message(request, messages.ERROR, 'Username or password is not correct!')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
@superuser_allowed_only
def add_admins(request):
    if request.method == "POST":
        try:
            if 'make_admin' in request.POST:
                username = request.POST.get('username')
                user = User.objects.get(username=username)
                user.groups.clear()

                group = Group.objects.get(name='admin')
                user.groups.add(group)
            elif 'remove_admin' in request.POST:
                username = request.POST.get('username')
                user = User.objects.get(username=username)
                user.groups.clear()

                group = Group.objects.get(name='user')
                user.groups.add(group)
            else:
                username = request.POST.get('username')
                User.objects.filter(username=username).delete()

        except Exception as e:
            return HttpResponse("Something went wrong.")

    users = list(User.objects.all())

    context = {
        'users': users,
    }
    return render(request,'add_admin.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def order_history(request):
    username = request.user.username
    all_orders = Orders.objects.filter(username=username).all().values()
    orders = []

    for order in all_orders:
        date = datetime.datetime.strftime(order['date'], '%Y-%m-%d %H:%M')
        order_price = order['order_price']
        order_dict = {'date': date,
                      'order_price': order_price}

        books = []
        for book in order['books_info'].split('\n'):
            book_info = book.split(' ')
            if len(book_info) != 1:
                books.append({'book_name': book_info[0], 'author': book_info[1], 'price': book_info[2], 'amount': book_info[3]})

        order_dict['books'] = books
        orders.append(order_dict)

    context = {'orders': orders}

    return render(request, 'order_history.html', context)

@login_required
def cart(request):

    template = loader.get_template('cart.html')
    cart = Cart(request)
    books_ids = request.session['cart']['books']
    books = []
    context = {}
    order_price = 0

    for book_id in set(books_ids):
        count = books_ids.count(book_id)
        book = Books.objects.filter(id=book_id)
        total_price = int(count) * int(book[0].price)

        order_price += total_price

        books.append({'book': book, 'count': count, 'total_price': total_price})

    context['order_price'] = order_price

    if request.method == 'POST':
        date = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(hours=5)
                                          , "%Y-%m-%d %H:%M")

        books_info = ""
        for book in books:
            book_info = book['book'][0]
            books_info += book_info.name + " " + book_info.author + " " + str(book_info.price) + " " + str(book['count']) + \
                          " " + str(book['total_price'])
            books_info += "\n"

        order = Orders(username=request.user.username, date=date, order_price=order_price, books_info=books_info)
        order.save()

        cart.clear()
        return redirect('home')

    context['books'] = books
    return HttpResponse(template.render(context, request))


def generate_books(request):
    for i in range(50):
        book = Books(name=f'bbboooobb', author=f'fedya{i}', price=1000 + i)
        book.save()
    return HttpResponse("Done")


def all_books(request):
    i = 0
    j = 4
    prev_available, next_available = 1, 1

    if request.method == "POST":
        if 'rmv_button' in request.POST:
            try:
                b_id = request.POST.get("rmv_button")
                Books.objects.filter(id=b_id).delete()
                return HttpResponseRedirect("/books/")

            except ObjectDoesNotExist as e:
                return HttpResponse("Model object doesn't exist.")

        elif 'new_name' in request.POST:
            try:
                n_name = request.POST.get("new_name")
                n_author = request.POST.get("new_author")
                n_price = request.POST.get("new_price")
                names = list(Books.objects.values('name'))

                if n_name in [x['name'] for x in names]:
                    return HttpResponse("Book with this name already exists.")

                if int(n_price) < 0:
                    raise ValueError

                new_book = Books(name=n_name, author=n_author, price=n_price)
                new_book.save()

            except ValueError as e:
                return HttpResponse("Enter a valid price.")

        elif 'add_to_cart' in request.POST:
            book_id = request.POST.get('add_to_cart')
            user_cart = Cart(request)
            user_cart.add(book_id)


        elif 'nxt' in request.POST:
            try:
                rmng = int(request.POST.get("rmng"))
                i = int(request.POST.get("nxt"))
                if rmng - i > 0:
                    i += 4
                elif rmng > 0:
                    j = i - rmng + 1
                    i += 4

            except Exception as e:
                return HttpResponse("Something gone wrong (nxt).")

        elif 'prev' in request.POST:
            try:
                i = int(request.POST.get("prev"))
                if i != 0:
                    i -= 4

            except Exception as e:
                return HttpResponse("Something gone wrong (prev).")

        elif 'filter_submit_button' in request.POST:
            selects = request.POST.dict()
            print(selects)

            for key in selects.keys():
                if selects[key] != '' and key != 'csrfmiddlewaretoken':
                    request.session['filter_type'] = key.split('_')[0]
                    request.session['filter_value'] = selects[key]
                    request.session['filtered_books'] = True
                    break

        elif 'reset_filters' in request.POST:
            request.session['filtered_books'] = False
            return redirect('books')

        else:
            try:
                b_id = request.POST.get("book_id")
                b_name = request.POST.get("book_name")
                b_author = request.POST.get("book_author")
                b_price = request.POST.get("book_price")

                book = Books.objects.filter(id=b_id)[0]
                book.name = b_name
                book.author = b_author
                book.price = b_price
                book.save()
            except ValueError as e:
                return HttpResponse("Something gone wrong. (Try to check price field again)")

    if request.session['filtered_books']:
        if request.session['filter_type'] == 'name':
            data = Books.objects.filter(name=f'{request.session['filter_value']}').values()
        elif request.session['filter_type'] == 'author':
            data = Books.objects.filter(author=f'{request.session['filter_value']}').values()
    else:
        data = Books.objects.all().values()

    remaining_books = data.count() - i - 4

    if i == 0: prev_available = False
    if remaining_books + 4 <= 4: next_available = False

    template = loader.get_template("books.html")
    context = {
        'books': data[i: i + j],
        'prev_i': i,
        'remaining_books': remaining_books,
        'prev_available': prev_available,
        'next_available': next_available,
    }
    print(request.user)
    return HttpResponse(template.render(context, request))


@login_required
@allowed_users(allowed_roles=['admin'])
def edit_book(request):
    book_id = request.GET.get('id', '0')

    book = Books.objects.filter(id=book_id).values()
    template = loader.get_template('edit_book.html')
    context = {
        'book': book,
    }
    return HttpResponse(template.render(context, request))


@login_required
def add_book(request):
    template = loader.get_template("add_book.html")
    context = {}
    return HttpResponse(template.render(context, request))


@login_required
def profile_view(request):
    template = loader.get_template("profile.html")
    context = {'username': request.user.username,
               'email': request.user.email}

    if request.user.name:
        context['name'] = request.user.name

    return HttpResponse(template.render(context, request))


@login_required
def edit_profile(request):

    if request.method == "POST":
        username = request.user.username
        user = User.objects.filter(username=username)[0]

        if 'new_password' in request.POST:
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            if confirm_new_password != new_password:
                messages.add_message(request, messages.ERROR, "Passwords don't match.", extra_tags='psw')
            else:
                user.set_password(new_password)
                user.save()

                return redirect('login')
        else:
            users = User.objects.all()
            usernames, emails = [x.username for x in users], [x.email for x in users]

            new_username = request.POST.get('username')
            new_email = request.POST.get('email')

            if user.name:
                new_name = request.POST.get('name')
            else:
                new_name = ''

            if new_username != username or new_email != user.email:
                if new_username not in usernames or new_email not in emails:
                    user.username = new_username
                    user.email = new_email
                    if new_name: user.name = new_name

                    user.save()
                    messages.add_message(request, messages.SUCCESS, 'Success!', extra_tags='inf')
                else:
                    messages.add_message(request, messages.ERROR, 'This username or email email already exists.', extra_tags='inf')

    template = loader.get_template('edit_profile.html')

    context = {
        'username': request.user.username,
        'email': request.user.email
        }

    if request.user.name: context['name'] = request.user.name

    return HttpResponse(template.render(context, request))









