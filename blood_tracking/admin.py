from django.contrib import admin
from .models import BloodUnit, BloodDonation, BloodTransfer


@admin.register(BloodUnit)
class BloodUnitAdmin(admin.ModelAdmin):
    list_display = ['unit_id', 'donor', 'blood_type', 'status', 'collected_at', 'expiry_date', 'current_hospital']
    list_filter = ['status', 'blood_type', 'collected_at', 'hiv_test', 'hepatitis_test']
    search_fields = ['unit_id', 'donor__user__first_name', 'donor__user__last_name', 'blood_type']
    readonly_fields = ['unit_id', 'created_at', 'updated_at', 'status_history']
    
    fieldsets = (
        ('Unit Identification', {
            'fields': ('unit_id', 'donor', 'blood_type')
        }),
        ('Collection & Expiry', {
            'fields': ('collected_at', 'expiry_date')
        }),
        ('Location & Status', {
            'fields': ('current_hospital', 'status')
        }),
        ('Test Results', {
            'fields': ('hiv_test', 'hepatitis_test')
        }),
        ('Blockchain Information', {
            'fields': ('blockchain_tx_hash',)
        }),
        ('Lifecycle History', {
            'fields': ('status_history',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'hospital', 'donation_date', 'status', 'blood_units', 'created_at']
    list_filter = ['status', 'donation_date', 'hospital']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'hospital__name']
    readonly_fields = ['created_at', 'updated_at', 'blockchain_hash']
    fieldsets = (
        ('Donation Information', {
            'fields': ('donor', 'hospital', 'donation_date', 'blood_units', 'status')
        }),
        ('Blockchain Information', {
            'fields': ('blockchain_hash',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BloodTransfer)
class BloodTransferAdmin(admin.ModelAdmin):
    list_display = ['donation', 'from_hospital', 'to_hospital', 'transfer_type', 'status', 'transfer_date']
    list_filter = ['status', 'transfer_type', 'transfer_date']
    search_fields = ['from_hospital__name', 'to_hospital__name', 'donation__donor__user__first_name']
    readonly_fields = ['created_at', 'updated_at', 'blockchain_hash']
    fieldsets = (
        ('Transfer Information', {
            'fields': ('donation', 'from_hospital', 'to_hospital', 'transfer_type', 'status')
        }),
        ('Transfer Dates', {
            'fields': ('transfer_date', 'received_date')
        }),
        ('Blockchain Information', {
            'fields': ('blockchain_hash',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
