from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.shop.models import Product
from .models import Wishlist


@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist/list.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        message = f'{product.name} added to your wishlist!'
        status = 'added'
    else:
        message = f'{product.name} is already in your wishlist.'
        status = 'exists'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': message,
            'status': status,
            'product_id': product_id
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Removed from wishlist'})

    messages.success(request, f'{product.name} removed from your wishlist.')
    return redirect('wishlist:wishlist_list')


@login_required
def add_to_cart_from_wishlist(request, product_id):
    from apps.cart.views import Cart
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)

    cart.add(product=product, quantity=1)
    messages.success(request, f'{product.name} added to cart!')

    # Remove from wishlist
    Wishlist.objects.filter(user=request.user, product=product).delete()

    return redirect('cart:cart_detail')