from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.shop.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))

    cart.add(product=product, quantity=quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'count': cart.get_count(),
            'total': str(cart.get_total_price())
        })

    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.success(request, 'Item removed from cart')
    return redirect('cart:cart_detail')


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared')
    return redirect('cart:cart_detail')


def cart_count(request):
    cart = Cart(request)
    return JsonResponse({'count': cart.get_count()})


@login_required
def checkout(request):
    cart = Cart(request)

    if cart.get_count() == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        from apps.orders.models import Order, OrderItem

        # Get form data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')

        # Validate required fields
        if not all([full_name, phone, address, city, state, postal_code, country]):
            messages.error(request, 'Please fill in all shipping information fields')
            return redirect('cart:checkout')

        # Create shipping address string
        shipping_address = f"{full_name}\n{address}\n{city}, {state} {postal_code}\n{country}\nPhone: {phone}"

        # Create order
        order = Order.objects.create(
            user=request.user,
            email=request.user.email,
            phone=phone,
            shipping_address=shipping_address,
            billing_address=shipping_address,
            payment_method=payment_method,
            subtotal=cart.get_total_price(),
            total_amount=cart.get_total_price(),
            status='pending',
            payment_status='pending'
        )

        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'].id,
                product_name=item['product'].name,
                quantity=item['quantity'],
                price=item['price'],
                total=item['total_price']
            )

            # Update product stock
            product = item['product']
            product.stock -= item['quantity']
            product.save()

        # Clear cart
        cart.clear()

        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('orders:order_detail', order_id=order.id)

    # GET request - show checkout page
    context = {
        'cart': cart,
        'cart_items': list(cart),
        'cart_total': cart.get_total_price(),
    }
    return render(request, 'cart/checkout.html', context)