from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class UserProfileManager(BaseUserManager):
    """Define a model manager for UserProfile with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'shopkeeper')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class UserProfile(AbstractUser):
    """Custom user model that extends the default User model."""
    USER_TYPES = (
        ('student', 'Student'),
        ('shopkeeper', 'Shopkeeper'),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserProfileManager()
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


class Product(models.Model):
    """Model for stationery products."""
    CATEGORY_CHOICES = [
        ('stationery', 'Stationery'),
        ('xerox', 'Xerox/Printing'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='stationery')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class PickupTimeSlot(models.Model):
    """Model for available pickup time slots."""
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_orders = models.PositiveIntegerField(default=10)
    current_orders = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%H:%M')}"
    
    def is_full(self):
        return self.current_orders >= self.max_orders


class Order(models.Model):
    """Model for customer orders."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders')
    pickup_slot = models.ForeignKey(PickupTimeSlot, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_code = models.CharField(max_length=10, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.student.username} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.pickup_code:
            # Generate a random 6-digit pickup code
            import random
            self.pickup_code = f"{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    def update_total_amount(self):
        """Update the total amount based on order items."""
        total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    """Model for items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} for Order #{self.order.id}"
    
    def subtotal(self):
        return self.quantity * self.price_at_time_of_order
    
    def save(self, *args, **kwargs):
        if not self.price_at_time_of_order:
            self.price_at_time_of_order = self.product.price
        super().save(*args, **kwargs)
        self.order.update_total_amount()
    
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.update_total_amount()
