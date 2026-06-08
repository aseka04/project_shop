from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=17, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    store_name = models.CharField(max_length=200, unique=True)
    store_slug = models.SlugField(max_length=200, unique=True)
    store_logo = models.ImageField(upload_to='stores/', null=True, blank=True)
    description = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.store_slug:
            self.store_slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name


class Address(models.Model):
    ADDRESS_TYPES = (
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='shipping')
    full_name = models.CharField(max_length=200)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}"