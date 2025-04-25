from django.urls import path, include
from .views import *

urlpatterns = [
    path('', homePageView, name='home'),
    path('books/', all_books, name='books'),
    path('books/edit/', edit_book, name='edit'),
    path('books/add/', add_book, name='add'),
    path('validate_username/', validate_username, name='check_username'),
    path('validate_email/', validate_email, name='check_email'),
    path('validate_password/', validate_password, name='check_password'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('login/', user_login, name='login'),
    path('spadmin/', add_admins, name='add_admin'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit_profile/', edit_profile, name='edit_profile'),
    path('cart', cart, name='cart'),
    path('order_history', order_history, name='order_history'),
    path('generate_books', generate_books),
]

