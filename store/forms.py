from django import forms
import re

class CheckoutForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
    )

    # Custom validation
    def clean_name(self):
        name = self.cleaned_data['name']
        if not re.match(r'^[A-Za-z ]+$', name):
            raise forms.ValidationError("Name must contain only letters and spaces.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\d{10}$', phone):
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone
