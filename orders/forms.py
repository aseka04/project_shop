from django import forms
from .models import Order
from apps.accounts.models import Address


class CheckoutForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Shipping address
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        widget=forms.RadioSelect,
        label="Shipping Address"
    )

    # New address fields
    address_line1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_line2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Payment
    payment_method = forms.ChoiceField(
        choices=[('stripe', 'Credit Card (Stripe)'), ('paypal', 'PayPal')],
        widget=forms.RadioSelect
    )

    save_address = forms.BooleanField(required=False, initial=True)
    terms_agreed = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['shipping_address'].queryset = Address.objects.filter(user=user)
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone_number


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'carrier', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'carrier': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Carrier'),
                ('usps', 'USPS'),
                ('fedex', 'FedEx'),
                ('ups', 'UPS'),
                ('dhl', 'DHL'),
            ]),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }