from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VendorProfile, Address
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'rating', 'total_sales', 'is_verified', 'is_active')
    list_filter = ('is_verified', 'is_active')
    search_fields = ('store_name', 'user__email')
    readonly_fields = ('rating', 'total_sales')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('full_name', 'address_line1', 'city')