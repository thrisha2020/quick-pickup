from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Order, Product, OrderItem

@staff_member_required
def admin_dashboard(request):
    # Get recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Calculate total revenue
    total_revenue = OrderItem.objects.aggregate(
        total=Sum('price')
    )['total'] or 0
    
    # Revenue for the current month
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = OrderItem.objects.filter(
        order__created_at__gte=this_month
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Count of products
    product_count = Product.objects.count()
    
    # Recent sales data for chart (last 7 days)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    daily_sales = Order.objects.filter(
        created_at__date__gte=week_ago,
        created_at__date__lte=today
    ).values('created_at__date').annotate(
        total=Sum('total_amount')
    ).order_by('created_at__date')
    
    context = {
        'title': 'Dashboard',
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'product_count': product_count,
        'daily_sales': list(daily_sales),
        'opts': {'app_label': 'admin'},  # Required for admin template
    }
    
    return render(request, 'admin/dashboard.html', context)
