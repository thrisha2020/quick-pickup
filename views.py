from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Order, OrderItem, PickupTimeSlot
from .serializers import (
    ProductSerializer, OrderWriteSerializer, OrderReadSerializer, PickupTimeSlotSerializer
)
from django.utils.crypto import get_random_string

# Add this view at the top of the file
def home(request):
    return render(request, 'index.html')

# --- 1. Product Catalog ViewSet (READ ONLY) ---
class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint for listing products."""
    queryset = Product.objects.all().order_by('category', 'name')
    serializer_class = ProductSerializer

# --- 2. Pickup Time Slot ViewSet (READ ONLY) ---
class PickupTimeSlotViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint for listing available pickup slots."""
    queryset = PickupTimeSlot.objects.all()
    serializer_class = PickupTimeSlotSerializer

# --- 3. Order ViewSet (Create and List by User) ---
class OrderViewSet(viewsets.GenericViewSet):
    """API endpoint for placing and viewing orders."""

    def get_queryset(self):
        """Filter orders by the logged-in user."""
        # Note: In a real Django setup, authentication would be enforced here.
        # For mock purposes, we'll assume a user ID is passed or mocked.
        return Order.objects.filter(student__username='student-xyz-123').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderWriteSerializer
        return OrderReadSerializer

    # POST /api/orders/
    def create(self, request):
        """Endpoint to place a new order."""
        # MOCK AUTH: Inject the student ID into the data for the serializer
        request.data['student'] = request.data.get('student_id', 1) # Assuming PK 1 exists for 'student-xyz-123'
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Return the read view for the newly created order
        read_serializer = OrderReadSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    # GET /api/orders/my_orders/
    @action(detail=False, methods=['get'], url_path='my_orders')
    def my_orders(self, request):
        """Lists orders belonging to the current user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
