from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.shop import views

urlpatterns = [
    # Direct view - no redirect
    path('', views.product_list, name='home'),
    path('admin/', admin.site.urls),

    # App includes
    path('shop/', include('apps.shop.urls', namespace='shop')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('wishlist/', include('apps.wishlist.urls')),  # Add this line
    path('reviews/', include('apps.reviews.urls')),
    path('chat/', include('apps.chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)