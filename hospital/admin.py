from django.contrib import admin
from .models import Hospital, BloodInventory, BloodRequest


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'phone_number', 'registration_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Hospital Information', {
            'fields': ('name', 'registration_number', 'admin')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'website')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'blood_type', 'quantity', 'expiry_date', 'last_updated']
    list_filter = ['blood_type', 'hospital', 'expiry_date']
    search_fields = ['hospital__name', 'blood_type']
    readonly_fields = ['last_updated']


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'blood_type', 'units_needed', 'urgency_level', 'status', 'created_at']
    list_filter = ['status', 'blood_type', 'urgency_level', 'created_at']
    search_fields = ['hospital__name', 'blood_type', 'description']
    readonly_fields = ['created_at', 'fulfilled_at']
    fieldsets = (
        ('Request Information', {
            'fields': ('hospital', 'blood_type', 'units_needed', 'description')
        }),
        ('Status Information', {
            'fields': ('status', 'urgency_level')
        }),
        ('Fulfillment Information', {
            'fields': ('fulfilled_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
