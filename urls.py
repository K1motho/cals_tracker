from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_food, name='add_food'),
    path('delete/<int:food_id>/', views.delete_food, name='delete_food'),
    path('reset/', views.reset_day, name='reset_day'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
