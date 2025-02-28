from logging import exception

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Books
from django.template import loader
from django.contrib.auth import login, authenticate
# from .forms import RegistrationForm

# Create your views here.
def homePageView(request):
    template = loader.get_template("index.html")
    context = {}
    return HttpResponse(template.render(context, request))


def all_books(request):
    i = 0
    j = 4
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
                return HttpResponse("Price has to be a positive number.")

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

    template = loader.get_template("books.html")
    context = {
        'books': data[i: i + j],
        'prev_i': i,
        'remaining_books': remaining_books,
    }
    return HttpResponse(template.render(context, request))

def edit_book(request):
    book_id = request.GET.get('id', '0')

    book = Books.objects.filter(id=book_id).values()
    template = loader.get_template('edit_book.html')
    context = {
        'book': book,
    }
    return HttpResponse(template.render(context, request))

def add_book(request):
    template = loader.get_template("add_book.html")
    context = {}
    return HttpResponse(template.render(context, request))
