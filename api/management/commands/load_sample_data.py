from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile, Product, PickupTimeSlot
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Loads sample data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create a shopkeeper user
        shopkeeper = User.objects.create_user(
            username='shopkeeper1',
            email='shop@example.com',
            password='shop1234',
            first_name='Shop',
            last_name='Keeper'
        )
        UserProfile.objects.create(
            user=shopkeeper,
            user_type='shopkeeper',
            phone_number='1234567890'
        )
        
        # Create some products
        products = [
            {'name': 'Notebook', 'price': 50.00, 'stock': 100, 'description': '200 pages notebook'},
            {'name': 'Pen', 'price': 10.00, 'stock': 200, 'description': 'Blue ballpoint pen'},
            {'name': 'Pencil', 'price': 5.00, 'stock': 300, 'description': 'HB Pencil'},
            {'name': 'Eraser', 'price': 5.00, 'stock': 150, 'description': 'White eraser'},
            {'name': 'Stapler', 'price': 120.00, 'stock': 30, 'description': 'Standard stapler'},
        ]
        
        for product_data in products:
            Product.objects.create(**product_data)
        
        # Create pickup time slots for the next 7 days
        now = timezone.now()
        for day in range(7):
            date = now + timedelta(days=day)
            for hour in range(9, 18):  # 9 AM to 6 PM
                start_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=30)
                PickupTimeSlot.objects.create(
                    start_time=start_time,
                    end_time=end_time,
                    max_orders=10,
                    current_orders=0
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data!'))
