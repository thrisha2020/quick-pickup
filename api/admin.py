from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile, Product, PickupTimeSlot, Order, OrderItem

User = get_user_model()

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    list_per_page = 20
    date_hierarchy = 'date_joined'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description', 'category')
    list_editable = ('price', 'is_available')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'is_available')
        }),
        ('Images', {
            'fields': ('image', 'thumbnail_preview'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />'.format(obj.image.url))
        return "No image"
    thumbnail_preview.short_description = 'Thumbnail Preview'
    readonly_fields = ('thumbnail_preview', 'created_at', 'updated_at')

class PickupTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_time', 'end_time', 'current_orders', 'max_orders', 'is_available')
    list_filter = ('is_available', 'start_time')
    date_hierarchy = 'start_time'
    list_editable = ('max_orders', 'is_available')
    search_fields = ('date', 'start_time', 'end_time')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Order Limits', {
            'fields': ('max_orders', 'current_orders')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price_at_time_of_order', 'subtotal')
    fields = ('product_name', 'quantity', 'price_at_time_of_order', 'subtotal')
    
    def product_name(self, instance):
        return instance.product.name
    product_name.short_description = 'Product'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_info', 'status_badge', 'total_amount', 'pickup_slot', 'created_at', 'order_actions')
    list_filter = ('status', 'created_at', 'pickup_slot__start_time')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'pickup_code')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'pickup_code', 'total_amount')
    list_select_related = ('student', 'pickup_slot')
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'pickup_slot')
    
    def student_info(self, obj):
        return f"{obj.student.get_full_name()} ({obj.student.email})"
    student_info.short_description = 'Student'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; border-radius: 10px; '
            'background: {}; color: white; font-size: 12px; font-weight: 500;">{}</span>',
            status_colors.get(obj.status, 'gray'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def order_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">View</a>',
            reverse('admin:api_order_change', args=[obj.id])
        )
    order_actions.short_description = 'Actions'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'product_name', 'quantity', 'price_at_time_of_order', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('product__name', 'order__id')
    list_select_related = ('order', 'product')
    list_per_page = 20
    
    def order_link(self, obj):
        url = reverse('admin:api_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def subtotal(self, obj):
        return f'${obj.quantity * obj.price_at_time_of_order:.2f}'
    subtotal.short_description = 'Subtotal'

# Register models with custom admin classes
admin.site.register(UserProfile, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(PickupTimeSlot, PickupTimeSlotAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
