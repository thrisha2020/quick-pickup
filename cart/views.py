from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from api.models import Product
import json

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, product_id):
    print(f"[DEBUG] Adding product {product_id} to cart for user {request.user.id}")
    
    try:
        # Get the product with select_for_update to lock the row
        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=product_id)
                print(f"[DEBUG] Found product: {product.name}, Available quantity: {getattr(product, 'quantity', 0)}")
                
                # Check if product is available and has stock
                if not product.is_available:
                    return JsonResponse(
                        {'success': False, 'error': 'This product is currently unavailable'}, 
                        status=400
                    )
                
                available_quantity = getattr(product, 'quantity', 0)
                if available_quantity <= 0:
                    return JsonResponse(
                        {'success': False, 'error': 'This product is out of stock'}, 
                        status=400
                    )
                
                # Get or create cart
                cart, created = Cart.objects.get_or_create(user=request.user)
                if created:
                    print("[DEBUG] Created new cart")
                
                # Get or create cart item
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': 1}
                )
                
                if not created:
                    # Check if adding one more would exceed available quantity
                    if cart_item.quantity >= available_quantity:
                        return JsonResponse({
                            'success': False, 
                            'error': f'Only {available_quantity} items available in stock',
                            'available_quantity': available_quantity
                        }, status=400)
                    
                    cart_item.quantity += 1
                    cart_item.save()
                
                # Update product quantity (if quantity field exists)
                if hasattr(product, 'quantity'):
                    product.quantity = max(0, product.quantity - 1)
                    product.save()
                
                # Refresh cart to get updated values
                cart.refresh_from_db()
                
                print(f"[DEBUG] Cart updated. Total items: {cart.total_items}, Subtotal: {cart.subtotal}")
                
                return JsonResponse({
                    'success': True,
                    'total_items': cart.total_items,
                    'subtotal': float(cart.subtotal),
                    'available_quantity': product.quantity if hasattr(product, 'quantity') else None
                })
                
        except Product.DoesNotExist:
            print(f"[ERROR] Product {product_id} not found")
            return JsonResponse(
                {'success': False, 'error': 'Product not found'}, 
                status=404
            )
            
    except Exception as e:
        print(f"[ERROR] Error in add_to_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {'success': False, 'error': str(e)}, 
            status=500
        )

@login_required
@require_POST
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        new_quantity = int(data.get('quantity', 1))
        
        if new_quantity < 1:
            return JsonResponse({'success': False, 'error': 'Quantity must be at least 1'}, status=400)
        
        with transaction.atomic():
            # Get the cart item with product details
            cart_item = get_object_or_404(
                CartItem.objects.select_related('product'), 
                id=item_id, 
                cart__user=request.user
            )
            
            # Check available quantity if product has quantity tracking
            if hasattr(cart_item.product, 'quantity'):
                # Calculate the difference in quantity
                quantity_difference = new_quantity - cart_item.quantity
                available_quantity = cart_item.product.quantity
                
                # If increasing quantity, check if enough stock is available
                if quantity_difference > 0 and available_quantity < quantity_difference:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Only {available_quantity} items available in stock',
                        'available_quantity': available_quantity
                    }, status=400)
                
                # Update the product quantity
                cart_item.product.quantity = max(0, cart_item.product.quantity - quantity_difference)
                cart_item.product.save()
            
            # Update the cart item quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            
            # Refresh the cart to get updated values
            cart_item.cart.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'total_items': cart_item.cart.total_items,
                'subtotal': float(cart_item.cart.subtotal),
                'item_total': float(cart_item.total_price),
                'available_quantity': cart_item.product.quantity if hasattr(cart_item.product, 'quantity') else None
            })
            
    except (ValueError, json.JSONDecodeError) as e:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
    except Exception as e:
        print(f"[ERROR] Error in update_cart_item: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {'success': False, 'error': 'An error occurred while updating the cart'}, 
            status=500
        )

@login_required
@require_POST
def remove_from_cart(request, item_id):
    try:
        with transaction.atomic():
            # Get the cart item with product details
            cart_item = get_object_or_404(
                CartItem.objects.select_related('product'), 
                id=item_id, 
                cart__user=request.user
            )
            
            # Restore the product quantity if the product has quantity tracking
            if hasattr(cart_item.product, 'quantity'):
                cart_item.product.quantity += cart_item.quantity
                cart_item.product.save()
            
            # Get cart reference before deleting the item
            cart = cart_item.cart
            
            # Delete the cart item
            cart_item.delete()
            
            # Refresh the cart to get updated values
            cart.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'total_items': cart.total_items,
                'subtotal': float(cart.subtotal)
            })
            
    except Exception as e:
        print(f"[ERROR] Error in remove_from_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {'success': False, 'error': 'An error occurred while removing the item from cart'}, 
            status=500
        )

def cart_summary(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal) if cart.subtotal else 0
        })
    return JsonResponse({'total_items': 0, 'subtotal': 0})
