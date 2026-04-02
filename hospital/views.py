from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Hospital, BloodInventory, BloodRequest
from .serializers import (
    HospitalSerializer, HospitalCreateSerializer, BloodInventorySerializer,
    BloodRequestSerializer, BloodRequestDetailSerializer
)


class HospitalViewSet(viewsets.ModelViewSet):
    """ViewSet for Hospital management"""
    queryset = Hospital.objects.filter(is_active=True)
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'email', 'phone_number', 'registration_number']
    
    def get_serializer_class(self):
        """Use simplified serializer for create action"""
        if self.action == 'create':
            return HospitalCreateSerializer
        return HospitalSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new hospital.
        
        Request body:
        {
            "name": "City Hospital",
            "address": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "country": "USA",
            "postal_code": "02101",
            "phone_number": "+1-555-0001",
            "email": "contact@cityhospital.com",
            "registration_number": "REG-001",
            "website": "https://cityhospital.com"
        }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def blood_availability(self, request, pk=None):
        """Get blood availability for a specific hospital"""
        hospital = self.get_object()
        inventory = hospital.blood_inventory.all()
        serializer = BloodInventorySerializer(inventory, many=True)
        return Response({
            'hospital': hospital.name,
            'inventory': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def blood_requests(self, request, pk=None):
        """Get blood requests for a specific hospital"""
        hospital = self.get_object()
        requests = hospital.blood_requests.all()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            requests = requests.filter(status=status_filter)
        
        serializer = BloodRequestDetailSerializer(requests, many=True)
        return Response({
            'hospital': hospital.name,
            'requests': serializer.data,
            'count': requests.count()
        })
    
    @action(detail=False, methods=['get'])
    def verified_hospitals(self, request):
        """Get all verified hospitals"""
        hospitals = Hospital.objects.filter(is_verified=True, is_active=True)
        serializer = self.get_serializer(hospitals, many=True)
        return Response({
            'count': hospitals.count(),
            'results': serializer.data
        })


class BloodInventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Inventory management"""
    queryset = BloodInventory.objects.all()
    serializer_class = BloodInventorySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available_inventory(self, request):
        """Get current blood inventory across all hospitals"""
        blood_type = request.query_params.get('blood_type')
        if blood_type:
            inventory = BloodInventory.objects.filter(blood_type=blood_type, quantity__gt=0)
        else:
            inventory = BloodInventory.objects.filter(quantity__gt=0)
        serializer = self.get_serializer(inventory, many=True)
        return Response({
            'count': inventory.count(),
            'results': serializer.data
        })


class BloodRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Request management"""
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hospital__name', 'blood_type']
    ordering_fields = ['created_at', 'urgency_level']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return BloodRequestDetailSerializer
        return BloodRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new blood request.
        
        Request body:
        {
            "hospital": 1,
            "blood_type": "O+",
            "units_needed": "10.00",
            "urgency_level": "critical",
            "description": "Emergency surgery scheduled"
        }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Blood request created successfully',
                'request': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def open_requests(self, request):
        """
        List all open blood requests.
        
        Query parameters:
        - blood_type: Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
        - urgency_level: Filter by urgency (critical, urgent, normal)
        - hospital: Filter by hospital ID
        
        Examples:
        GET /api/blood-requests/open_requests/
        GET /api/blood-requests/open_requests/?blood_type=O+
        GET /api/blood-requests/open_requests/?urgency_level=critical
        GET /api/blood-requests/open_requests/?blood_type=A+&urgency_level=urgent
        """
        requests = BloodRequest.objects.filter(status='open')
        
        # Filter by blood type
        blood_type = request.query_params.get('blood_type')
        if blood_type:
            requests = requests.filter(blood_type=blood_type)
        
        # Filter by urgency level
        urgency = request.query_params.get('urgency_level')
        if urgency:
            requests = requests.filter(urgency_level=urgency)
        
        # Filter by hospital
        hospital_id = request.query_params.get('hospital')
        if hospital_id:
            requests = requests.filter(hospital_id=hospital_id)
        
        serializer = BloodRequestDetailSerializer(requests, many=True)
        return Response({
            'count': requests.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_blood_type(self, request):
        """
        Get open blood requests filtered by blood type.
        
        Query parameter:
        - blood_type (required): Blood type to filter by
        
        Example: GET /api/blood-requests/by_blood_type/?blood_type=O+
        """
        blood_type = request.query_params.get('blood_type')
        if not blood_type:
            return Response(
                {'error': 'blood_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        requests = BloodRequest.objects.filter(status='open', blood_type=blood_type)
        serializer = BloodRequestDetailSerializer(requests, many=True)
        return Response({
            'blood_type': blood_type,
            'count': requests.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update the status of a blood request.
        
        Request body:
        {
            "status": "fulfilled|cancelled"
        }
        
        When marking as fulfilled, fulfilled_at will be set to current time.
        """
        blood_request = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = ['open', 'fulfilled', 'cancelled']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'status must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        blood_request.status = new_status
        
        # Set fulfilled_at if marking as fulfilled
        if new_status == 'fulfilled' and not blood_request.fulfilled_at:
            blood_request.fulfilled_at = timezone.now()
        
        blood_request.save()
        
        serializer = BloodRequestDetailSerializer(blood_request)
        return Response({
            'message': f'Status updated to {new_status}',
            'request': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def critical_requests(self, request):
        """Get all critical priority open blood requests"""
        requests = BloodRequest.objects.filter(
            status='open',
            urgency_level='critical'
        ).order_by('-created_at')
        
        serializer = BloodRequestDetailSerializer(requests, many=True)
        return Response({
            'count': requests.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def hospital_requests(self, request):
        """Get blood requests for the authenticated user's hospital (if applicable)"""
        hospital_id = request.query_params.get('hospital_id')
        
        if not hospital_id:
            return Response(
                {'error': 'hospital_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            hospital = Hospital.objects.get(id=hospital_id)
            requests = hospital.blood_requests.all()
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                requests = requests.filter(status=status_filter)
            
            serializer = BloodRequestDetailSerializer(requests, many=True)
            return Response({
                'hospital': hospital.name,
                'count': requests.count(),
                'results': serializer.data
            })
        except Hospital.DoesNotExist:
            return Response(
                {'error': 'Hospital not found'},
                status=status.HTTP_404_NOT_FOUND
            )
