from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ShopkeeperOrderView, ShopkeeperSignupView, AdminSignupView

# Create a router for our API endpoints
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'time-slots', views.PickupTimeSlotViewSet, basename='timeslot')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('auth/shopkeeper/signup/', ShopkeeperSignupView.as_view(), name='shopkeeper-signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.UserView.as_view(), name='user'),
    
    # Custom endpoints
    path('time-slots/available/', views.AvailableTimeSlotsView.as_view(), name='available-time-slots'),
    path('orders/shopkeeper/', ShopkeeperOrderView.as_view(), name='shopkeeper-orders'),
    path('orders/<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
]
