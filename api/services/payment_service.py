import stripe
import razorpay
from decimal import Decimal
from django.conf import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize Razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_stripe_payment_intent(amount, currency='inr', metadata=None):
    """Create a Stripe PaymentIntent"""
    try:
        # Convert amount to smallest currency unit (paise for INR)
        amount_in_paise = int(Decimal(amount) * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency=currency,
            metadata=metadata or {}
        )
        return {
            'client_secret': intent.client_secret,
            'id': intent.id
        }
    except Exception as e:
        print(f"Error creating payment intent: {str(e)}")
        return None

def verify_stripe_payment(payment_intent_id):
    """Verify a Stripe payment"""
    try:
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return None

def create_razorpay_order(amount, currency='INR', receipt=None, notes=None):
    """Create a Razorpay order"""
    try:
        # Convert amount to smallest currency unit (paise for INR)
        amount_in_paise = int(Decimal(amount) * 100)
        
        order_data = {
            'amount': amount_in_paise,
            'currency': currency,
            'payment_capture': '1'  # Auto-capture payment
        }
        
        if receipt:
            order_data['receipt'] = receipt
        if notes:
            order_data['notes'] = notes
            
        return razorpay_client.order.create(data=order_data)
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

def verify_razorpay_payment(order_id, payment_id, signature):
    """Verify a Razorpay payment signature"""
    try:
        return razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
    except Exception as e:
        print(f"Error verifying Razorpay payment: {str(e)}")
        return False
