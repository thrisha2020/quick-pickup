from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import UserProfile, Product, PickupTimeSlot, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'user_type', 'phone_number')
    
    def create(self, validated_data):
        # Extract profile data
        user_type = validated_data.pop('user_type', 'student')
        phone_number = validated_data.pop('phone_number', '')
        
        # Create user
        validated_data['password'] = make_password(validated_data['password'])
        user = super().create(validated_data)
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            user_type=user_type,
            phone_number=phone_number
        )
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number')
        read_only_fields = ('id', 'user_type')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PickupTimeSlotSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PickupTimeSlot
        fields = '__all__'
        read_only_fields = ('current_orders', 'is_available')

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_time_of_order', 'subtotal')
        read_only_fields = ('order', 'price_at_time_of_order', 'subtotal')
    
    def get_subtotal(self, obj):
        return obj.subtotal()
    
    def create(self, validated_data):
        # Set the price at the time of order
        product = validated_data['product']
        validated_data['price_at_time_of_order'] = product.price
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    pickup_slot_details = PickupTimeSlotSerializer(source='pickup_slot', read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'student', 'pickup_slot', 'pickup_slot_details', 'status', 
            'status_display', 'pickup_code', 'total_amount', 'created_at', 
            'updated_at', 'items'
        )
        read_only_fields = ('pickup_code', 'total_amount', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        # Ensure the pickup slot is available
        pickup_slot = validated_data.get('pickup_slot')
        if pickup_slot and pickup_slot.is_full():
            raise serializers.ValidationError("This time slot is already full.")
        
        # Create the order
        order = Order.objects.create(**validated_data)
        
        # Update the pickup slot's current_orders
        if pickup_slot:
            pickup_slot.current_orders += 1
            pickup_slot.save()
        
        return order
