from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/edit/<int:pk>/', views.address_edit, name='address_edit'),
    path('addresses/delete/<int:pk>/', views.address_delete, name='address_delete'),
    path('orders/', views.order_history, name='order_history'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]