from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from apps.shop.models import Product
from apps.orders.models import Order


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if user already reviewed
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('shop:product_detail', id=product.id, slug=product.slug)

    # Check if user purchased this product
    has_purchased = Order.objects.filter(
        user=request.user,
        items__product=product,
        status='delivered'
    ).exists()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified_purchase = has_purchased
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('shop:product_detail', id=product.id, slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'reviews/form.html', {'form': form, 'product': product})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('shop:product_detail', id=review.product.id, slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/form.html', {'form': form, 'product': review.product, 'is_edit': True})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('shop:product_detail', id=product.id, slug=product.slug)