from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1,
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px;'}))
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError('Quantity must be at least 1')
        if quantity > 99:
            raise forms.ValidationError('Quantity cannot exceed 99')
        return quantity