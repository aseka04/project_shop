from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, F
from django.http import JsonResponse
from .models import Category, Product, ProductImage, ProductVariant, ProductSpecification, RecentlyViewed
from .forms import ProductSearchForm, VendorProductForm, ProductVariantForm
from apps.accounts.models import VendorProfile
from apps.reviews.models import Review
from apps.wishlist.models import Wishlist
from apps.cart.cart import Cart


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(available=True, stock__gt=0)

    # Category filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Search functionality
    query = request.GET.get('query')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Get featured products for sidebar
    featured_products = Product.objects.filter(featured=True, available=True)[:5]

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    # Get reviews
    from apps.reviews.models import Review
    reviews = Review.objects.filter(product=product, is_approved=True)[:10]

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    return render(request, 'shop/product/detail.html', context)


def deals_page(request):
    # Products with discounts (compare_price > price)
    deals_products = Product.objects.filter(
        available=True,
        compare_price__isnull=False
    ).exclude(compare_price__lte=F('price'))[:12]

    return render(request, 'shop/deals.html', {'deals_products': deals_products})


def bestsellers_page(request):
    # Best selling products (ordered by total_sold)
    best_sellers = Product.objects.filter(
        available=True,
        total_sold__gt=0
    ).order_by('-total_sold')[:12]

    categories = Category.objects.filter(is_active=True)

    # Top rated products
    top_rated = Product.objects.filter(
        available=True,
        average_rating__gt=0
    ).order_by('-average_rating')[:5]

    return render(request, 'shop/bestsellers.html', {
        'best_sellers': best_sellers,
        'categories': categories,
        'top_rated': top_rated,
    })


def contact_page(request):
    if request.method == 'POST':
        # Here you would send email or save to database
        from django.contrib import messages
        messages.success(request, 'Message sent successfully!')
        return redirect('shop:contact')

    return render(request, 'shop/contact.html')
@login_required
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor_profile
    except:
        messages.error(request, 'You are not a vendor.')
        return redirect('shop:product_list')

    products = vendor.products.all()

    # Statistics
    total_products = products.count()
    total_orders = sum(product.total_sold for product in products)
    total_revenue = sum(float(product.price) * product.total_sold for product in products)
    average_rating = products.aggregate(Avg('average_rating'))['average_rating__avg'] or 0

    context = {
        'vendor': vendor,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_rating': average_rating,
        'products': products[:10],
    }
    return render(request, 'shop/vendor/dashboard.html', context)


@login_required
def vendor_product_list(request):
    try:
        vendor = request.user.vendor_profile
    except:
        messages.error(request, 'You are not a vendor.')
        return redirect('shop:product_list')

    products = vendor.products.all().order_by('-created_at')

    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'shop/vendor/product_list.html', {'products': products})


@login_required
def vendor_product_add(request):
    try:
        vendor = request.user.vendor_profile
    except:
        messages.error(request, 'You are not a vendor.')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = VendorProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()

            messages.success(request, 'Product added successfully!')
            return redirect('shop:vendor_product_list')
    else:
        form = VendorProductForm()

    return render(request, 'shop/vendor/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def vendor_product_edit(request, product_id):
    try:
        vendor = request.user.vendor_profile
        product = get_object_or_404(Product, id=product_id, vendor=vendor)
    except:
        messages.error(request, 'Product not found or you don\'t have permission.')
        return redirect('shop:vendor_product_list')

    if request.method == 'POST':
        form = VendorProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('shop:vendor_product_list')
    else:
        form = VendorProductForm(instance=product)

    variants = product.variants.all()
    variant_form = ProductVariantForm()

    return render(request, 'shop/vendor/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'product': product,
        'variants': variants,
        'variant_form': variant_form
    })


@login_required
def vendor_product_delete(request, product_id):
    try:
        vendor = request.user.vendor_profile
        product = get_object_or_404(Product, id=product_id, vendor=vendor)
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    except:
        messages.error(request, 'Product not found.')

    return redirect('shop:vendor_product_list')


def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(tags__icontains=query),
            available=True
        )[:10]

        suggestions = [{'name': p.name, 'url': p.get_absolute_url(), 'price': str(p.price)} for p in products]
        return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})