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
    path('spadmin/', add_admins, name='add_admin'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit_profile/', edit_profile, name='edit_profile'),
    path('cart', cart, name='cart'),
    path('order_history', order_history, name='order_history')
]

