from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegistrationForm, UserProfileForm, AddressForm
from .models import Address
from apps.orders.models import Order


def user_register(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'shop:product_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('shop:product_list')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'user': request.user})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add Address'})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(pk=address.pk).update(
                    is_default=False)
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('accounts:address_list')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.info(request, 'If an account exists with that email, you will receive password reset instructions.')
        return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')