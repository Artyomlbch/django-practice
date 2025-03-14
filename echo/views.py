from logging import exception

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Books, User
from django.template import loader
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomCreationForm, LoginForm
from .decorators import unauthenticated_user, allowed_users, superuser_allowed_only



# Create your views here.
def homePageView(request):
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

def logout_view(request):
    logout(request)
    return redirect('home')

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
