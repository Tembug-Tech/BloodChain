from django.contrib import admin
from .models import Badge, DonorBadge, Points, PointTransaction, Reward, RewardRedemption, RewardToken


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_reward', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(DonorBadge)
class DonorBadgeAdmin(admin.ModelAdmin):
    list_display = ['donor', 'badge', 'earned_date']
    list_filter = ['badge', 'earned_date']
    search_fields = ['donor__user__first_name', 'donor__user__last_name']
    readonly_fields = ['earned_date']


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    list_display = ['donor', 'total_points', 'available_points', 'updated_at']
    search_fields = ['donor__user__first_name', 'donor__user__last_name']
    readonly_fields = ['updated_at']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['points', 'points_amount', 'source', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['points__donor__user__first_name', 'description']
    readonly_fields = ['created_at']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_cost', 'quantity_available', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ['donor', 'reward', 'points_spent', 'status', 'redemption_date']
    list_filter = ['status', 'redemption_date']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'reward__name']
    readonly_fields = ['redemption_date']


@admin.register(RewardToken)
class RewardTokenAdmin(admin.ModelAdmin):
    list_display = ['donor', 'amount', 'reward_type', 'created_at', 'transaction_hash']
    list_filter = ['reward_type', 'created_at']
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'transaction_hash']
    readonly_fields = ['transaction_hash', 'created_at']
