from django.conf import settings

class Cart(object):
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            cart['books'] = []

        self.cart = cart


    def add(self, book_id):
        books = self.cart['books']

        books.append(book_id)
        self.session.update({'cart': {'books': books}})


    def clear(self):
        books = self.cart['books']
        self.session.update({'cart': {'books': []}})



