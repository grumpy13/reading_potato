from django.urls import path
from authentication import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name="register"),
    path('signin/', views.signin , name="signin"),
    path('signout/', views.signout , name="signout"),
]