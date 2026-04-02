from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BloodUnitViewSet, BloodDonationViewSet, BloodTransferViewSet

router = DefaultRouter()
router.register(r'units', BloodUnitViewSet, basename='blood-unit')
router.register(r'donations', BloodDonationViewSet, basename='donation')
router.register(r'transfers', BloodTransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]
