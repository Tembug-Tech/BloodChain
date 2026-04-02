from django.contrib import admin
from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_type', 'location', 'is_available', 'created_at']
    list_filter = ['blood_type', 'is_available', 'location', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone_number', 'location']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Blood Information', {
            'fields': ('blood_type',)
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'location')
        }),
        ('Donation Information', {
            'fields': ('is_available', 'last_donation_date')
        }),
        ('Blockchain Information', {
            'fields': ('wallet_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
