from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import models
from .models import UserProfile, Product, PickupTimeSlot, Order, OrderItem
from .serializers import (
    UserSerializer, UserProfileSerializer, ProductSerializer, 
    PickupTimeSlotSerializer, OrderSerializer, OrderItemSerializer
)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=request.data.get('user_type', 'student'),
                phone_number=request.data.get('phone_number', '')
            )
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password1')
        password2 = request.data.get('password2')
        
        if not all([username, email, password, password2]):
            return Response(
                {'error': 'All fields are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if password != password2:
            return Response(
                {'error': 'Passwords do not match'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create superuser (admin)
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type='ADMIN',
                phone_number=''  # Can be updated later
            )
            
            # Log the user in
            login(request, user)
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'is_admin': True
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShopkeeperSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password1')
        password2 = request.data.get('password2')
        
        if not all([username, email, password, password2]):
            return Response(
                {'error': 'All fields are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if password != password2:
            return Response(
                {'error': 'Passwords do not match'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True  # Shopkeepers have staff status
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type='SHOPKEEPER',
                phone_number=request.data.get('phone_number', '')
            )
            
            # Log the user in
            login(request, user)
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'is_shopkeeper': True
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response(status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view products
    
    def get_queryset(self):
        # Return all available products, ordered by creation date
        return Product.objects.filter(is_available=True).order_by('-created_at')
    
    def get_permissions(self):
        # Only require authentication for write operations
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class PickupTimeSlotViewSet(viewsets.ModelViewSet):
    queryset = PickupTimeSlot.objects.filter(is_available=True)
    serializer_class = PickupTimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show future time slots
        return queryset.filter(start_time__gte=timezone.now())
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available time slots that are not full."""
        queryset = self.get_queryset()
        available_slots = [slot for slot in queryset if not slot.is_full()]
        serializer = self.get_serializer(available_slots, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own orders unless they're staff
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(student=self.request.user)
    
    def perform_create(self, serializer):
        # Set the student to the current user
        order = serializer.save(student=self.request.user)
        
        # Send order confirmation email
        self._send_order_confirmation(order)
        
        # Send order confirmation SMS if phone number exists
        try:
            profile = order.student.userprofile
            if profile.phone_number:
                from .utils.sms_service import send_sms
                message = (f"Your order #{order.id} has been received. "
                         f"Total: ₹{order.total_amount}. "
                         f"Pickup code: {order.pickup_code}")
                send_sms(profile.phone_number, message)
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
    
    def _send_order_confirmation(self, order):
        """Send order confirmation email to the customer."""
        from .utils.email_service import send_email
        
        context = {
            'user': order.student,
            'order': order,
            'order_items': order.items.all(),
            'order_date': order.created_at.strftime("%B %d, %Y"),
        }
        
        send_email(
            to_email=order.student.email,
            subject=f"Order Confirmation #{order.id}",
            template_name='order_confirmation',
            context=context
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        # Send status update email
        if new_status in ['ready_for_pickup', 'completed']:
            self._send_status_update_email(order, new_status)
        
        return Response({'status': 'Status updated'})
    
    def _send_status_update_email(self, order, status):
        """Send status update email to the customer."""
        from .utils.email_service import send_email
        
        status_display = dict(Order.STATUS_CHOICES).get(status, status)
        
        context = {
            'user': order.student,
            'order': order,
            'status': status_display,
            'order_items': order.items.all(),
        }
        
        send_email(
            to_email=order.student.email,
            subject=f"Order #{order.id} is now {status_display}",
            template_name='status_update',
            context=context
        )
    
    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        """Create a Stripe payment intent for the order."""
        from .services.payment_service import create_stripe_payment_intent
        
        order = self.get_object()
        
        # Ensure the order belongs to the requesting user
        if order.student != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Not authorized to access this order'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create payment intent
        payment_intent = create_stripe_payment_intent(
            amount=float(order.total_amount),
            metadata={
                'order_id': order.id,
                'user_id': request.user.id
            }
        )
        
        if not payment_intent:
            return Response(
                {'error': 'Failed to create payment intent'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(payment_intent)
    
    @action(detail=True, methods=['post'])
    def create_razorpay_order(self, request, pk=None):
        """Create a Razorpay order for the order."""
        from .services.payment_service import create_razorpay_order
        
        order = self.get_object()
        
        # Ensure the order belongs to the requesting user
        if order.student != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Not authorized to access this order'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create Razorpay order
        razorpay_order = create_razorpay_order(
            amount=float(order.total_amount),
            receipt=f"order_{order.id}",
            notes={
                'order_id': order.id,
                'user_id': request.user.id
            }
        )
        
        if not razorpay_order:
            return Response(
                {'error': 'Failed to create Razorpay order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(razorpay_order)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

class AvailableTimeSlotsView(APIView):
    """View to list all available pickup time slots."""
    
    def get(self, request, format=None):
        """Return a list of all available time slots."""
        now = timezone.now()
        time_slots = PickupTimeSlot.objects.filter(
            start_time__gte=now,
            is_available=True
        ).exclude(
            current_orders__gte=models.F('max_orders')
        ).order_by('start_time')
        
        serializer = PickupTimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data)

class UpdateOrderStatusView(APIView):
    """View to update the status of an order."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Update the status of an order."""
        order = get_object_or_404(Order, pk=pk)
        
        # Check if the user is a shopkeeper
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'shopkeeper':
            return Response(
                {'error': 'Only shopkeepers can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the order status
        order.status = new_status
        order.save(update_fields=['status'])
        
        return Response({
            'message': f'Order status updated to {order.get_status_display()}',
            'status': order.status
        })


class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for OrderItem model."""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Shopkeepers can see all order items, users can only see their own
        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'shopkeeper':
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__student=user)
    
    def perform_create(self, serializer):
        # Ensure the order belongs to the current user
        order_id = self.request.data.get('order')
        order = get_object_or_404(Order, id=order_id, student=self.request.user)
        serializer.save(order=order)


class ShopkeeperOrderView(generics.ListAPIView):
    """
    View for shopkeepers to view and manage orders with filtering and search capabilities.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['student__username', 'student__email', 'pickup_code']
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only shopkeepers can access this view
        if not (self.request.user.is_staff or 
               (hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.user_type == 'shopkeeper')):
            return Order.objects.none()
            
        queryset = Order.objects.select_related('student', 'pickup_slot')
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__email__icontains=search) |
                Q(student__username__icontains=search) |
                Q(pickup_code__iexact=search)
            )
            
        return queryset
