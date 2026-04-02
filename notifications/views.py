from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import send_emergency_alert, mark_notification_as_read, get_unread_notifications_count


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification management"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the current user"""
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = get_unread_notifications_count(request.user)
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        updated_count = 0
        for notification in notifications:
            mark_notification_as_read(notification)
            updated_count += 1
        
        return Response({
            'message': 'All notifications marked as read',
            'updated_count': updated_count
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific notification as read"""
        try:
            notification = self.get_object()
            if notification.recipient != request.user:
                return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
            mark_notification_as_read(notification)
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def send_emergency_alert(self, request):
        """
        Send emergency alert notifications to available donors.
        
        Request body:
        {
            "blood_type": "O+",
            "location": "New York, NY"
        }
        """
        blood_type = request.data.get('blood_type')
        location = request.data.get('location')
        
        if not blood_type or not location:
            return Response(
                {'error': 'blood_type and location are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            notifications = send_emergency_alert(blood_type, location)
            serializer = self.get_serializer(notifications, many=True)
            return Response({
                'message': f'Emergency alert sent to {len(notifications)} donors',
                'notifications': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """ViewSet for notification preference management"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    
    def list(self, request):
        """Get notification preferences for current user"""
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)
    
    def update(self, request):
        """Update notification preferences"""
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
