from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Donor
from .serializers import DonorSerializer, DonorRegistrationSerializer


class DonorViewSet(viewsets.ModelViewSet):
    """ViewSet for Donor management"""
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['register', 'create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new donor with user account.
        
        Required fields:
        - username
        - email
        - password
        - blood_type (A+, A-, B+, B-, AB+, AB-, O+, O-)
        - phone_number
        - location
        - date_of_birth (YYYY-MM-DD)
        
        Optional fields:
        - first_name
        - last_name
        - is_available (default: true)
        - wallet_address
        """
        serializer = DonorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                donor = serializer.save()
                donor_serializer = DonorSerializer(donor)
                return Response(
                    {
                        'message': 'Donor registered successfully',
                        'donor': donor_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get the current user's donor profile"""
        try:
            donor = Donor.objects.get(user=request.user)
            serializer = self.get_serializer(donor)
            return Response(serializer.data)
        except Donor.DoesNotExist:
            return Response(
                {'error': 'Donor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_availability(self, request, pk=None):
        """
        Update donor availability status.
        
        Request body:
        {
            "is_available": true/false
        }
        """
        donor = self.get_object()
        
        # Verify user can only update their own availability
        if donor.user != request.user:
            return Response(
                {'error': 'You can only update your own availability'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_available = request.data.get('is_available')
        if is_available is None:
            return Response(
                {'error': 'is_available parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        donor.is_available = is_available
        donor.save()
        
        serializer = self.get_serializer(donor)
        return Response({
            'message': f'Availability updated to {is_available}',
            'donor': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        List available donors filtered by blood type and/or location.
        
        Query parameters:
        - blood_type: Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
        - location: Filter by location (partial match, case-insensitive)
        
        Examples:
        - /api/donors/available/?blood_type=O+
        - /api/donors/available/?location=New York
        - /api/donors/available/?blood_type=A+&location=California
        """
        queryset = Donor.objects.filter(is_available=True)
        
        # Filter by blood type
        blood_type = request.query_params.get('blood_type')
        if blood_type:
            queryset = queryset.filter(blood_type=blood_type)
        
        # Filter by location
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_blood_type(self, request):
        """
        Get available donors by blood type.
        
        Query parameters:
        - blood_type (required): Blood type to filter by (A+, A-, B+, B-, AB+, AB-, O+, O-)
        
        Example: /api/donors/by_blood_type/?blood_type=O+
        """
        blood_type = request.query_params.get('blood_type')
        if not blood_type:
            return Response(
                {'error': 'blood_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        donors = Donor.objects.filter(
            blood_type=blood_type,
            is_available=True
        )
        serializer = self.get_serializer(donors, many=True)
        return Response({
            'blood_type': blood_type,
            'count': donors.count(),
            'results': serializer.data
        })
