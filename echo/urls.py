from django.urls import path, include
from .views import *

urlpatterns = [
    path('', homePageView, name='home'),
    path('books/', all_books, name='books'),
    path('books/edit/', edit_book, name='edit'),
    path('books/add/', add_book, name='add'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('login/', user_login, name='login'),
    path('spadmin/', add_admins, name='add_admin')
]

