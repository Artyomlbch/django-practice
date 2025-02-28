# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import Users
#
# class RegistrationForm(UserCreationForm):
#     email = forms.EmailField(max_length=254, help_text="Required. Add a valid email address.")
#     name = forms.CharField(max_length=30)
#
#     class Meta:
#         model = Users
#         fields = ('username', 'email', 'password1', 'password2', 'name')
#
#     def clean_username(self):
#         username = self.cleaned_data['username']
#
#         try:
#             user = Users.objects.get(username=username)
#
#         except Exception as e:
#             return username
#
#         raise forms.ValidationError(f"Username '{username}' is already in use.")
#
#     def clean_email(self):
#         email = self.cleaned_data['email']
#
#         try:
#             user = Users.objects.get(email=email)
#
#         except Exception as e:
#             return email
#
#         raise forms.ValidationError(f"Email '{email}' is already in use.")