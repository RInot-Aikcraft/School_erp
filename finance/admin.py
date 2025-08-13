from django.contrib import admin
from .models import FeeType, FeeStructure, Fee, PaymentMethod, Payment

@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'fee_type', 'amount', 'academic_year')
    list_filter = ('academic_year', 'classroom', 'fee_type')
    search_fields = ('classroom__name', 'fee_type__name')

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_due', 'amount_paid', 'balance', 'status')
    list_filter = ('status', 'fee_structure__academic_year', 'fee_structure__classroom')
    search_fields = ('student__first_name', 'student__last_name', 'fee_structure__fee_type__name')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('fee', 'amount', 'payment_method', 'payment_date', 'reference')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('fee__student__first_name', 'fee__student__last_name', 'reference')