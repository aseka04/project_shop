from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('deals/', views.deals_page, name='deals'),
    path('bestsellers/', views.bestsellers_page, name='bestsellers'),
    path('contact/', views.contact_page, name='contact'),

    # Vendor URLs
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_product_list, name='vendor_product_list'),
    path('vendor/products/add/', views.vendor_product_add, name='vendor_product_add'),
    path('vendor/products/edit/<int:product_id>/', views.vendor_product_edit, name='vendor_product_edit'),
    path('vendor/products/delete/<int:product_id>/', views.vendor_product_delete, name='vendor_product_delete'),

    # AJAX
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]