from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_list, name='wishlist_list'),
    path('add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),
]