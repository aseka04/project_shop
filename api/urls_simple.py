from django.urls import path
from . import simple_views

app_name = 'api'

urlpatterns = [
    path('', simple_views.api_root, name='api_root'),
    path('products/', simple_views.products_list, name='products'),
    path('auth/register/', simple_views.register, name='register'),
    path('auth/login/', simple_views.login, name='login'),
]