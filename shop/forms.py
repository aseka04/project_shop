from django import forms
from .models import Product, ProductVariant, Category

class ProductSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search products...'}))
    min_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sort_by = forms.ChoiceField(required=False, choices=[
        ('-created_at', 'Newest'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
        ('-average_rating', 'Top Rated'),
        ('-total_sold', 'Best Selling'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))

class VendorProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'short_description', 'price',
                 'compare_price', 'stock', 'condition', 'weight', 'dimensions', 'tags']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'compare_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'value', 'price_adjustment', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'price_adjustment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }