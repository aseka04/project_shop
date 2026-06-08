from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'  # Add this line

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'users', views.UserViewSet)
router.register(r'addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.register_user, name='api_register'),
    path('auth/login/', views.login_user, name='api_login'),
    path('cart/', views.get_cart, name='api_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='api_cart_add'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='api_cart_remove'),
    path('wishlist/', views.wishlist_api, name='api_wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_api, name='api_wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='api_wishlist_remove'),
    path('search/', views.search_products, name='api_search'),
]