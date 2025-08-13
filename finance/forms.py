from django import forms
from .models import FeeType, FeeStructure, Fee, PaymentMethod, Payment

class FeeTypeForm(forms.ModelForm):
    class Meta:
        model = FeeType
        fields = ['name', 'description', 'code']

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['classroom', 'fee_type', 'amount', 'academic_year']

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference', 'notes']