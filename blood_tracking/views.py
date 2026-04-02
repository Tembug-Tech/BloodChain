from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import BloodUnit, BloodDonation, BloodTransfer
from .serializers import (
    BloodUnitSerializer, BloodUnitDetailSerializer, BloodUnitCreateSerializer,
    BloodUnitStatusUpdateSerializer, BloodDonationSerializer, BloodTransferSerializer
)
from .blockchain_service import get_blockchain_service


class BloodUnitViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Unit tracking with blockchain integration"""
    queryset = BloodUnit.objects.all()
    serializer_class = BloodUnitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['unit_id', 'donor__user__first_name', 'donor__user__last_name', 'blood_type']
    ordering_fields = ['collected_at', 'expiry_date', 'created_at']
    ordering = ['-collected_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blockchain_service = get_blockchain_service()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create' or self.action == 'register':
            return BloodUnitCreateSerializer
        elif self.action == 'retrieve':
            return BloodUnitDetailSerializer
        elif self.action in ['update_status', 'update_blockchain_status']:
            return BloodUnitStatusUpdateSerializer
        return BloodUnitSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new blood unit and record on blockchain"""
        serializer = BloodUnitCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            instance = serializer.save()
            
            # Record on blockchain if donor has wallet
            blockchain_result = None
            if instance.donor.wallet_address:
                blockchain_result = self.blockchain_service.record_blood_unit_on_chain(
                    unit_id=str(instance.unit_id),
                    blood_type=instance.blood_type,
                    donor_wallet=instance.donor.wallet_address
                )
                
                if blockchain_result and blockchain_result.get('success'):
                    instance.blockchain_tx_hash = blockchain_result.get('tx_hash')
                    instance.save()
            
            response_data = BloodUnitDetailSerializer(instance).data
            response_data['blockchain_record'] = blockchain_result
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def blockchain_history(self, request, pk=None):
        """Get full blockchain history of a blood unit"""
        from django.shortcuts import get_object_or_404
        unit = get_object_or_404(BloodUnit, pk=pk)
        
        # Get blockchain data
        blockchain_data = self.blockchain_service.get_unit_history(str(unit.unit_id))
        
        return Response({
            'unit_id': str(unit.unit_id),
            'blood_type': unit.blood_type,
            'donor': {
                'name': unit.donor.user.get_full_name(),
                'wallet': unit.donor.wallet_address,
            },
            'blockchain': blockchain_data,
            'local_status_history': unit.status_history if unit.status_history else [],
            'blockchain_tx_hash': unit.blockchain_tx_hash,
            'tests': {
                'hiv_test': unit.hiv_test,
                'hepatitis_test': unit.hepatitis_test
            }
        })
    
    @action(detail=True, methods=['patch'])
    def update_blockchain_status(self, request, pk=None):
        """Update blood unit status on both local database and blockchain"""
        from django.shortcuts import get_object_or_404
        unit = get_object_or_404(BloodUnit, pk=pk)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {'error': 'status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update blockchain
        blockchain_result = self.blockchain_service.update_unit_status_on_chain(
            unit_id=str(unit.unit_id),
            new_status=new_status
        )
        
        # Update local database
        old_status = unit.status
        unit.status = new_status
        
        # Record status change
        history_entry = {
            'previous_status': old_status,
            'new_status': new_status,
            'timestamp': timezone.now().isoformat(),
            'blockchain_tx_hash': blockchain_result.get('tx_hash') if blockchain_result else None,
            'notes': request.data.get('notes', '')
        }
        
        if not unit.status_history:
            unit.status_history = []
        unit.status_history.append(history_entry)
        unit.save()
        
        return Response({
            'message': f'Blood unit status updated from {old_status} to {new_status}',
            'unit_id': str(unit.unit_id),
            'blockchain_result': blockchain_result,
            'unit': BloodUnitDetailSerializer(unit).data
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update blood unit status (local database only)"""
        unit = self.get_object()
        serializer = BloodUnitStatusUpdateSerializer(unit, data=request.data, partial=True)
        
        if serializer.is_valid():
            old_status = unit.status
            new_status = request.data.get('status', unit.status)
            
            # Add to status history
            if new_status != old_status:
                history_entry = {
                    'previous_status': old_status,
                    'new_status': new_status,
                    'timestamp': timezone.now().isoformat(),
                    'notes': request.data.get('notes', '')
                }
                if not unit.status_history:
                    unit.status_history = []
                unit.status_history.append(history_entry)
            
            serializer.save()
            return Response({
                'message': f'Blood unit status updated from {old_status} to {new_status}',
                'unit': BloodUnitDetailSerializer(unit).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def lifecycle_history(self, request):
        """Get full lifecycle history of a blood unit"""
        unit_id = request.query_params.get('unit_id')
        if not unit_id:
            return Response(
                {'error': 'unit_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.shortcuts import get_object_or_404
        unit = get_object_or_404(BloodUnit, unit_id=unit_id)
        
        serializer = BloodUnitDetailSerializer(unit)
        return Response({
            'unit_id': str(unit.unit_id),
            'donor': unit.donor.user.get_full_name(),
            'blood_type': unit.blood_type,
            'collected_at': unit.collected_at,
            'expiry_date': unit.expiry_date,
            'lifecycle_history': serializer.data.get('lifecycle_summary'),
            'status_transitions': {
                'current_status': unit.status,
                'history': unit.status_history if unit.status_history else []
            },
            'tests': {
                'hiv_test': unit.hiv_test,
                'hepatitis_test': unit.hepatitis_test
            },
            'blockchain_tx_hash': unit.blockchain_tx_hash,
            'current_hospital': unit.current_hospital.id if unit.current_hospital else None,
            'created_at': unit.created_at,
            'updated_at': unit.updated_at
        })
    
    @action(detail=False, methods=['get'])
    def by_blood_type(self, request):
        """Get available blood units filtered by blood type"""
        blood_type = request.query_params.get('blood_type')
        if not blood_type:
            return Response(
                {'error': 'blood_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        units = BloodUnit.objects.filter(
            blood_type=blood_type,
            status='storage'  # Only available units in storage
        ).select_related('donor', 'current_hospital')
        
        serializer = self.get_serializer(units, many=True)
        return Response({
            'blood_type': blood_type,
            'count': units.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def available_units(self, request):
        """Get all available blood units in storage"""
        units = BloodUnit.objects.filter(status='storage').select_related('donor', 'current_hospital')
        
        serializer = self.get_serializer(units, many=True)
        return Response({
            'count': units.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def units_at_location(self, request):
        """Get blood units at a specific location/hospital"""
        location_id = request.query_params.get('location_id')
        if not location_id:
            return Response(
                {'error': 'location_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        units = BloodUnit.objects.filter(
            current_hospital_id=location_id
        ).select_related('donor', 'current_hospital')
        
        serializer = self.get_serializer(units, many=True)
        return Response({
            'location_id': location_id,
            'count': units.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def near_expiry(self, request):
        """Get blood units that are expiring soon (within 7 days)"""
        from datetime import timedelta
        near_expiry_date = timezone.now() + timedelta(days=7)
        
        units = BloodUnit.objects.filter(
            status='storage',
            expiry_date__lte=near_expiry_date,
            expiry_date__gt=timezone.now()
        ).select_related('donor', 'current_hospital').order_by('expiry_date')
        
        serializer = self.get_serializer(units, many=True)
        return Response({
            'threshold_days': 7,
            'count': units.count(),
            'results': serializer.data
        })


class BloodDonationViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Donation tracking"""
    queryset = BloodDonation.objects.all()
    serializer_class = BloodDonationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['donor__user__first_name', 'donor__user__last_name', 'hospital__name']
    ordering_fields = ['donation_date', 'created_at']
    ordering = ['-donation_date']
    
    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        """Get current user's donations"""
        try:
            donor = request.user.donor_profile
            donations = BloodDonation.objects.filter(donor=donor)
            serializer = self.get_serializer(donations, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'User is not a donor'}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get donations filtered by status"""
        status = request.query_params.get('status')
        if not status:
            return Response({'error': 'status parameter is required'}, status=400)
        donations = BloodDonation.objects.filter(status=status)
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)


class BloodTransferViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Transfer tracking"""
    queryset = BloodTransfer.objects.all()
    serializer_class = BloodTransferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['from_hospital__name', 'to_hospital__name', 'transfer_type']
    ordering_fields = ['transfer_date', 'created_at']
    ordering = ['-transfer_date']
    
    @action(detail=False, methods=['get'])
    def pending_transfers(self, request):
        """Get all pending transfers"""
        transfers = BloodTransfer.objects.filter(status='pending')
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_received(self, request, pk=None):
        """Mark a transfer as received"""
        transfer = self.get_object()
        transfer.status = 'received'
        transfer.received_date = timezone.now()
        transfer.save()
        serializer = self.get_serializer(transfer)
        return Response(serializer.data)
