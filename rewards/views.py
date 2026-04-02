from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Badge, DonorBadge, Points, Reward, RewardRedemption, RewardToken
from .serializers import (
    BadgeSerializer, DonorBadgeSerializer, PointsSerializer,
    RewardSerializer, RewardRedemptionSerializer, RewardTokenSerializer
)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Badge management"""
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]


class DonorBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Donor Badge management"""
    serializer_class = DonorBadgeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get badges for the current user's donor profile"""
        try:
            donor = self.request.user.donor_profile
            return DonorBadge.objects.filter(donor=donor)
        except:
            return DonorBadge.objects.none()


class PointsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Points management"""
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_points(self, request):
        """Get current user's points"""
        try:
            donor = request.user.donor_profile
            points = Points.objects.get(donor=donor)
            serializer = self.get_serializer(points)
            return Response(serializer.data)
        except:
            return Response({'error': 'Points not found'}, status=404)


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Reward management"""
    queryset = Reward.objects.filter(is_active=True)
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get rewards by category"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': 'category parameter is required'}, status=400)
        rewards = Reward.objects.filter(category=category, is_active=True)
        serializer = self.get_serializer(rewards, many=True)
        return Response(serializer.data)


class RewardRedemptionViewSet(viewsets.ModelViewSet):
    """ViewSet for Reward Redemption management"""
    serializer_class = RewardRedemptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get redemptions for the current user's donor profile"""
        try:
            donor = self.request.user.donor_profile
            return RewardRedemption.objects.filter(donor=donor)
        except:
            return RewardRedemption.objects.none()
    
    @action(detail=False, methods=['post'])
    def redeem_reward(self, request):
        """Redeem a reward"""
        reward_id = request.data.get('reward_id')
        quantity = request.data.get('quantity', 1)
        
        if not reward_id:
            return Response({'error': 'reward_id is required'}, status=400)
        
        try:
            donor = request.user.donor_profile
            reward = Reward.objects.get(id=reward_id)
            points = Points.objects.get(donor=donor)
            
            total_cost = reward.points_cost * quantity
            if points.available_points < total_cost:
                return Response({'error': 'Insufficient points'}, status=400)
            
            redemption = RewardRedemption.objects.create(
                donor=donor,
                reward=reward,
                points_spent=total_cost,
                quantity=quantity,
                status='pending'
            )
            
            serializer = self.get_serializer(redemption)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def pending_redemptions(self, request):
        """Get pending redemptions"""
        try:
            donor = request.user.donor_profile
            redemptions = RewardRedemption.objects.filter(donor=donor, status='pending')
            serializer = self.get_serializer(redemptions, many=True)
            return Response(serializer.data)
        except:
            return Response([])


class RewardTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Reward Token blockchain management"""
    serializer_class = RewardTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get reward tokens for the current user's donor profile"""
        try:
            donor = self.request.user.donor_profile
            return RewardToken.objects.filter(donor=donor).order_by('-created_at')
        except:
            return RewardToken.objects.none()
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get total token balance for current user"""
        try:
            from django.db.models import Sum
            donor = request.user.donor_profile
            balance = RewardToken.objects.filter(donor=donor).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            return Response({
                'success': True,
                'wallet': donor.wallet_address,
                'balance': balance,
                'donor_id': donor.id
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    @action(detail=False, methods=['get'])
    def transaction_history(self, request):
        """Get reward token transaction history for current user"""
        try:
            from django.db.models import Sum
            
            donor = request.user.donor_profile
            tokens = self.get_queryset()
            
            # Get pagination parameters
            page_size = int(request.query_params.get('page_size', 20))
            page = int(request.query_params.get('page', 1))
            
            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size
            
            # Get total count and amount
            total_count = tokens.count()
            total_amount = tokens.aggregate(total=Sum('amount'))['total'] or 0
            
            # Get paginated results
            paginated_tokens = tokens[start:end]
            
            serializer = self.get_serializer(paginated_tokens, many=True)
            
            return Response({
                'success': True,
                'wallet': donor.wallet_address,
                'transactions': serializer.data,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size
                },
                'totals': {
                    'total_transactions': total_count,
                    'total_amount': total_amount
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    @action(detail=False, methods=['post'])
    def issue_token(self, request):
        """Issue reward tokens (admin action)"""
        from .services import issue_reward_token
        
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Only staff members can issue tokens'
            }, status=403)
        
        try:
            donor_id = request.data.get('donor_id')
            amount = request.data.get('amount')
            reward_type = request.data.get('reward_type', 'donation_reward')
            
            if not donor_id or not amount:
                return Response({
                    'success': False,
                    'error': 'donor_id and amount are required'
                }, status=400)
            
            # Get donor and wallet address
            from donor.models import Donor
            try:
                donor = Donor.objects.get(id=donor_id)
            except Donor.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Donor not found'
                }, status=404)
            
            # Issue tokens
            result = issue_reward_token(
                donor.wallet_address,
                amount,
                reward_type,
                donor
            )
            
            if not result['success']:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to issue tokens')
                }, status=400)
            
            # Serialize the created token
            token = result['reward_token']
            serializer = self.get_serializer(token)
            
            return Response({
                'success': True,
                'message': f'Issued {amount} {reward_type} tokens to donor {donor_id}',
                'token': serializer.data,
                'transaction_hash': result['tx_hash']
            }, status=201)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get reward tokens filtered by reward type"""
        reward_type = request.query_params.get('reward_type')
        
        if not reward_type:
            return Response({
                'success': False,
                'error': 'reward_type parameter is required'
            }, status=400)
        
        try:
            from django.db.models import Sum
            
            tokens = self.get_queryset().filter(reward_type=reward_type)
            total_amount = tokens.aggregate(total=Sum('amount'))['total'] or 0
            
            serializer = self.get_serializer(tokens, many=True)
            
            return Response({
                'success': True,
                'reward_type': reward_type,
                'count': tokens.count(),
                'total_amount': total_amount,
                'tokens': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
