from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BadgeViewSet, DonorBadgeViewSet, PointsViewSet,
    RewardViewSet, RewardRedemptionViewSet, RewardTokenViewSet
)

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'donor-badges', DonorBadgeViewSet, basename='donor-badge')
router.register(r'points', PointsViewSet, basename='points')
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'reward-redemptions', RewardRedemptionViewSet, basename='reward-redemption')
router.register(r'reward-tokens', RewardTokenViewSet, basename='reward-token')

urlpatterns = [
    path('', include(router.urls)),
]
