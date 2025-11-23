from flask import current_app, Flask, jsonify, json, render_template, request, redirect, session, url_for, flash
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# -------Stripe incorporation-------
import stripe
# -------END OF Stripe incorporation-------

# Load environment variables from .env file
load_dotenv()

# Import db from models.py
from models import db, User, Payment, Subscription

# -------Stripe incorporation-------
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe.api_version = '2025-10-29.clover'
# -------END OF Stripe incorporation-------

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///payment_prototype.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment/one-time', methods=['GET'])
def one_time_payment():
    """Show the one-time payment form with embedded Stripe Checkout"""
    # -------Stripe incorporation-------
    # Get publishable key from environment for frontend
    stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    
    # Fetch price info from Stripe (optional - for display purposes)
    price_id = os.environ.get('STRIPE_PRICE_ID_ONE_TIME')
    price_info = None
    if price_id:
        try:
            price = stripe.Price.retrieve(price_id)
            # Convert amount from cents to dollars
            price_info = {
                'amount': price.unit_amount / 100,
                'currency': price.currency.upper()
            }
        except:
            pass  # If price fetch fails, just don't show price
    # -------END OF Stripe incorporation-------
    return render_template('one_time_payment.html', 
                         stripe_publishable_key=stripe_publishable_key,
                         price_info=price_info)

@app.route('/payment/subscribe', methods=['GET'])
def subscribe():
    """Show the subscription form with multiple tier options"""
    # -------Stripe incorporation-------
    # Get publishable key from environment for frontend
    stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    
    # Fetch price info for both tiers from Stripe
    one_price_id = os.environ.get('STRIPE_PRICE_ID_SUBS_ONE')
    two_price_id = os.environ.get('STRIPE_PRICE_ID_SUBS_TWO')
    
    one_price_info = None
    two_price_info = None
    
    if one_price_id:
        try:
            price = stripe.Price.retrieve(one_price_id)
            one_price_info = {
                'amount': price.unit_amount / 100,
                'currency': price.currency.upper(),
                'price_id': one_price_id
            }
        except:
            pass
    
    if two_price_id:
        try:
            price = stripe.Price.retrieve(two_price_id)
            two_price_info = {
                'amount': price.unit_amount / 100,
                'currency': price.currency.upper(),
                'price_id': two_price_id
            }
        except:
            pass
    # -------END OF Stripe incorporation-------
    
    return render_template('subscribe.html', 
                         stripe_publishable_key=stripe_publishable_key,
                         one_price_info=one_price_info,
                         two_price_info=two_price_info)

@app.route('/dashboard')
def dashboard():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('index'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    payments = Payment.query.filter_by(user_id=user.id).all()
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', user=user, payments=payments, subscriptions=subscriptions)

# ===================================================================
# Stripe Incorporaiton
# ===================================================================

# -------------------------------------------------------------------
# SECTION 1: CHECKOUT SESSION - ONE-TIME PAYMENT
# -------------------------------------------------------------------
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout Session for one-time payment"""
    try:
        email = request.form.get('email')
        name = request.form.get('name')
        
        if not email or not name:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('one_time_payment'))
        
        # Check if user exists, create if not
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
                
        # Get the base URL for return URL
        # request.host_url gives us the full URL (e.g., "http://localhost:5000/")
        # rstrip('/') removes trailing slash to avoid double slashes
        base_url = request.host_url.rstrip('/')
        
        # Get Price ID from environment variable (set in .env file)
        price_id = os.environ.get('STRIPE_PRICE_ID_ONE_TIME')
        
        if not price_id:
            flash('Price ID not configured. Please set STRIPE_PRICE_ID_ONE_TIME in .env', 'error')
            return redirect(url_for('one_time_payment'))
        
        # Create Stripe Checkout Session in EMBEDDED mode
        # ui_mode='embedded' keeps user on your site
        # Returns clientSecret for frontend to embed checkout
        checkout_session = stripe.checkout.Session.create(
            ui_mode='embedded',  
            customer_email=email,
            line_items=[{
                'price': price_id,  
                'quantity': 1,
            }],
            mode='payment',
            # For embedded mode, return_url is where to go after payment completes
            return_url=base_url + url_for('payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
            # Metadata: Store custom data we can retrieve later
            metadata={
                'user_id': user.id,        # Store user ID to find them when payment completes
                'payment_type': 'one_time' # Store payment type for verification
            }
        )
        
        # Return clientSecret for frontend to embed checkout
        # User stays on your site - checkout appears in an embedded container!
        return jsonify({'clientSecret': checkout_session.client_secret})
        
    except stripe.error.StripeError as e:
        # Return JSON error for AJAX request
        return jsonify({'error': f'Stripe error: {str(e)}'}), 400
    except Exception as e:
        # Return JSON error for AJAX request
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# -------------------------------------------------------------------
# SECTION 2: CHECKOUT SESSION - SUBSCRIPTION
# -------------------------------------------------------------------
@app.route('/create-subscription-checkout-session', methods=['POST'])
def create_subscription_checkout_session():
    """Create a Stripe Checkout Session for subscription"""
    try:
        email = request.form.get('email')
        name = request.form.get('name')
        plan_tier = request.form.get('plan_tier')  # 'one' or 'two'
        price_id_env_key = f'STRIPE_PRICE_ID_SUBS_{plan_tier.upper()}'
        price_id = os.environ.get(price_id_env_key)
        
        if not email or not name or not plan_tier:
            return jsonify({'error': 'Please fill in all fields and select a plan'}), 400
        
        if not price_id:
            return jsonify({'error': f'Price ID not configured for {plan_tier} plan. Please set {price_id_env_key} in .env'}), 400
        
        # Check if user exists, create if not
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
        
        # Check if user already has an active subscription
        active_subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if active_subscription:
            return jsonify({'error': 'You already have an active subscription'}), 400
        
        # Get the base URL for return URL
        base_url = request.host_url.rstrip('/')
        
        # Create Stripe Checkout Session in EMBEDDED mode for subscription
        checkout_session = stripe.checkout.Session.create(
            ui_mode='embedded',
            customer_email=email,
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            return_url=base_url + url_for('subscription_success') + '?session_id={CHECKOUT_SESSION_ID}',
            metadata={
                'user_id': user.id,
                'payment_type': 'subscription',
                'plan_tier': plan_tier
            }
        )
        
        # Return clientSecret for frontend to embed checkout
        return jsonify({'clientSecret': checkout_session.client_secret})
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# -------------------------------------------------------------------
# SECTION 3: WEBHOOK HANDLER
# -------------------------------------------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""

    # Obtains the raw body of the request → payload
    # (json as plain text ex.: 
    # { "id": "evt_123", "type": "checkout.session.completed", "data": {"object": { "id": "cs_123","amount_total": 2000}}})
    # Obtains the Stripe signature HTTP header → sig_header
    # Obtains your secret key for verifying the webhook → webhook_secret

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception as e:
        print(f'Webhook error: {str(e)}')
        return jsonify({'error': 'Webhook verification failed'}), 400
    
    # Handle the event
    event_type = event['type']
    event_data = event.get('data', {}).get('object', {})
    
    print(f'Received webhook event: {event_type}')
    
    try:
        if event_type == 'checkout.session.completed':
            # Handle successful checkout (both one-time and subscription)
            handle_checkout_completed(event_data)
        
        elif event_type == 'customer.subscription.created':
            # Subscription successfully created for the first time
            handle_subscription_created(event_data)
        
        elif event_type == 'customer.subscription.updated':
            # Subscription changed (upgrade/downgrade)
            handle_subscription_updated(event_data)
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled
            handle_subscription_deleted(event_data)
        
        elif event_type == 'invoice.payment_succeeded':
            # Subscription renewed successfully
            handle_invoice_payment_succeeded(event_data)
        
        elif event_type == 'invoice.payment_failed':
            # Subscription payment failed (optional - you mentioned you don't need this)
            # But I'll add it anyway in case you change your mind
            handle_invoice_payment_failed(event_data)
        
        elif event_type == 'customer.updated':
            # Customer information changed (name, email, address, default payment method, etc.)
            handle_customer_updated(event_data)
        
        elif event_type == 'payment_method.attached':
            # New payment method attached to customer
            handle_payment_method_attached(event_data)
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f'Error handling webhook event {event_type}: {str(e)}')
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------------
# SECTION 4: WEBHOOK HANDLER FUNCTIONS
# -------------------------------------------------------------------

def handle_checkout_completed(session):
    """
    Handle checkout.session.completed event
    
    This webhook fires for:
    - One-time payment success (creates Payment record)
    - Initial subscription checkout completion (subscription created via customer.subscription.created)
    """
    metadata = session.get('metadata', {})
    payment_type = metadata.get('payment_type')
    user_id = metadata.get('user_id')
    
    if payment_type == 'one_time' and user_id:
        # Handle one-time payment success via webhook (primary handler)
        user = User.query.get(int(user_id))
        if user:
            session_id = session.get('id')
            existing_payment = Payment.query.filter_by(
                user_id=user.id,
                payment_type='one_time',
                transaction_id=session_id
            ).first()
            
            if not existing_payment:
                amount = session.get('amount_total', 0) / 100
                payment = Payment(
                    user_id=user.id,
                    amount=amount,
                    payment_type='one_time',
                    status='completed',
                    transaction_id=session_id
                )
                db.session.add(payment)
                db.session.commit()
                print(f'One-time payment recorded: ${amount} for user {user_id}')

def handle_subscription_created(subscription):
    """Handle customer.subscription.created - subscription successfully made for the first time"""
    stripe_subscription_id = subscription.get('id')
    customer_id = subscription.get('customer')
    
    # Get customer email from Stripe
    try:
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get('email')
        
        if not email:
            print(f'No email found for customer {customer_id}')
            return
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f'User not found for email {email}')
            return
        
        # Check if subscription already exists
        existing_sub = Subscription.query.filter_by(
            stripe_subscription_id=stripe_subscription_id
        ).first()
        
        if existing_sub:
            print(f'Subscription {stripe_subscription_id} already exists')
            return
        
        # Get subscription details
        items = subscription.get('items', {}).get('data', [])
        if not items:
            print(f'No items found in subscription {stripe_subscription_id}')
            return
        
        price_id = items[0].get('price', {}).get('id')
        price_obj = stripe.Price.retrieve(price_id)
        amount = price_obj.get('unit_amount', 0) / 100
        
        # Determine plan tier from metadata or price ID
        metadata = subscription.get('metadata', {})
        plan_tier = metadata.get('plan_tier')
        if not plan_tier:
            # Try to infer from price ID environment variable names
            if 'BASIC' in price_id.upper() or os.environ.get('STRIPE_PRICE_ID_SUBS_BASIC') == price_id:
                plan_tier = 'basic'
            elif 'FANCY' in price_id.upper() or os.environ.get('STRIPE_PRICE_ID_SUBS_FANCY') == price_id:
                plan_tier = 'fancy'
            else:
                plan_tier = 'unknown'
        
        # Get dates
        start_date = datetime.fromtimestamp(subscription.get('current_period_start', 0))
        next_billing = datetime.fromtimestamp(subscription.get('current_period_end', 0))
        
        # Create subscription record
        new_subscription = Subscription(
            user_id=user.id,
            amount=amount,
            status=subscription.get('status', 'active'),
            plan_tier=plan_tier,
            stripe_subscription_id=stripe_subscription_id,
            stripe_price_id=price_id,
            start_date=start_date,
            next_billing_date=next_billing
        )
        db.session.add(new_subscription)
        db.session.commit()
        print(f'Subscription created: {plan_tier} tier, ${amount}/month for user {user.id}')
    except Exception as e:
        print(f'Error creating subscription: {str(e)}')

def handle_subscription_updated(subscription):
    """Handle customer.subscription.updated - subscription changed (upgrade/downgrade)"""
    stripe_subscription_id = subscription.get('id')
    
    # Find existing subscription
    existing_sub = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription_id
    ).first()
    
    if not existing_sub:
        print(f'Subscription {stripe_subscription_id} not found in database')
        return
    
    # Update subscription details
    items = subscription.get('items', {}).get('data', [])
    if items:
        price_id = items[0].get('price', {}).get('id')
        price_obj = stripe.Price.retrieve(price_id)
        amount = price_obj.get('unit_amount', 0) / 100
        
        existing_sub.amount = amount
        existing_sub.stripe_price_id = price_id
        
        # Update plan tier if changed
        metadata = subscription.get('metadata', {})
        plan_tier = metadata.get('plan_tier')
        if plan_tier:
            existing_sub.plan_tier = plan_tier
    
    # Update status
    existing_sub.status = subscription.get('status', 'active')
    
    # Update billing dates
    existing_sub.next_billing_date = datetime.fromtimestamp(
        subscription.get('current_period_end', 0)
    )
    
    db.session.commit()
    print(f'Subscription updated: {stripe_subscription_id}')

def handle_subscription_deleted(subscription):
    """Handle customer.subscription.deleted - subscription cancelled"""
    stripe_subscription_id = subscription.get('id')
    
    # Find existing subscription
    existing_sub = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription_id
    ).first()
    
    if not existing_sub:
        print(f'Subscription {stripe_subscription_id} not found in database')
        return
    
    # Mark as cancelled
    existing_sub.status = 'cancelled'
    existing_sub.cancelled_at = datetime.utcnow()
    
    db.session.commit()
    print(f'Subscription cancelled: {stripe_subscription_id}')

def handle_invoice_payment_succeeded(invoice):
    """Handle invoice.payment_succeeded - subscription renewed successfully"""
    subscription_id = invoice.get('subscription')
    
    if not subscription_id:
        # This might be a one-time payment invoice, skip it
        return
    
    # Find subscription
    existing_sub = Subscription.query.filter_by(
        stripe_subscription_id=subscription_id
    ).first()
    
    if not existing_sub:
        print(f'Subscription {subscription_id} not found for invoice payment')
        return
    
    # Update next billing date from the subscription
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        existing_sub.next_billing_date = datetime.fromtimestamp(
            subscription.get('current_period_end', 0)
        )
        existing_sub.status = 'active'  # Ensure it's active after successful payment
        db.session.commit()
        print(f'Subscription renewed: {subscription_id}')
    except Exception as e:
        print(f'Error updating subscription renewal: {e}')

def handle_invoice_payment_failed(invoice):
    """Handle invoice.payment_failed - subscription payment failed (optional)"""
    subscription_id = invoice.get('subscription')
    
    if not subscription_id:
        return
    
    # Find subscription
    existing_sub = Subscription.query.filter_by(
        stripe_subscription_id=subscription_id
    ).first()
    
    if not existing_sub:
        return
    
    # Update status to past_due or unpaid
    existing_sub.status = 'past_due'
    db.session.commit()
    print(f'Subscription payment failed: {subscription_id}')

def handle_customer_updated(customer):
    """Handle customer.updated - customer information changed"""
    customer_id = customer.get('id')
    email = customer.get('email')
    
    if not email:
        print(f'No email found for customer {customer_id}')
        return
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f'User not found for email {email}')
        return
    
    # Update user information
    name = customer.get('name')
    if name and name != user.name:
        user.name = name
        print(f'Updated name for user {user.id}: {user.name} -> {name}')
    
    # Note: Address, phone, and other fields would be stored here when added to User model
    # For now, we only update the name
    
    db.session.commit()
    print(f'Customer updated: {customer_id}')

def handle_payment_method_attached(payment_method):
    """Handle payment_method.attached - new payment method attached to customer"""
    payment_method_id = payment_method.get('id')
    customer_id = payment_method.get('customer')
    
    if not customer_id:
        print(f'No customer ID found for payment method {payment_method_id}')
        return
    
    # Get customer from Stripe to find user
    try:
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get('email')
        
        if not email:
            print(f'No email found for customer {customer_id}')
            return
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f'User not found for email {email}')
            return
        
        # Check if this is the default payment method
        default_payment_method = customer.get('invoice_settings', {}).get('default_payment_method')
        is_default = (default_payment_method == payment_method_id)
        
        # Note: Payment method details would be stored here when PaymentMethod model is added
        # For now, we just log the event
        print(f'Payment method {payment_method_id} attached to customer {customer_id} (user {user.id})')
        if is_default:
            print(f'Payment method {payment_method_id} is now the default payment method')
        
    except Exception as e:
        print(f'Error handling payment method attachment: {str(e)}')

# -------------------------------------------------------------------
# SECTION 5: SUCCESS ROUTES (Fallback for user redirects)
# These routes are fallbacks when users complete checkout and get redirected.
# The webhook handlers above are the primary source of truth for payment/subscription processing.
# -------------------------------------------------------------------

@app.route('/payment/success')
def payment_success():
    """
    Fallback route for one-time payment success (user redirect after checkout)
    
    NOTE: The primary handler is the webhook (checkout.session.completed).
    This route is a fallback for when users complete checkout and get redirected.
    The webhook is more reliable and should be the source of truth.
    """
    # Get session_id from URL query parameter
    # Stripe automatically adds this when redirecting: ?session_id=cs_test_abc123...
    # The {CHECKOUT_SESSION_ID} placeholder in return_url gets replaced by Stripe
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('No session ID provided', 'error')
        return redirect(url_for('index'))
    
    try:
        # Retrieve the checkout session from Stripe to verify payment
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get user from metadata
        user_id = checkout_session.metadata.get('user_id')
        payment_type = checkout_session.metadata.get('payment_type')
        
        if user_id and payment_type == 'one_time':
            user = User.query.get(int(user_id))
            if user:
                # Check if payment already recorded
                existing_payment = Payment.query.filter_by(
                    user_id=user.id,
                    payment_type='one_time',
                    transaction_id=session_id
                ).first()
                
                if not existing_payment:
                    # Get amount from checkout session (from Stripe, not hardcoded)
                    amount = checkout_session.amount_total / 100  # Convert from cents
                    
                    # Create payment record
                    payment = Payment(
                        user_id=user.id,
                        amount=amount,
                        payment_type='one_time',
                        status='completed',
                        transaction_id=session_id
                    )
                    db.session.add(payment)
                    db.session.commit()
        
        flash('Payment successful! Thank you for your payment.', 'success')
        return redirect(url_for('index'))
        
    except stripe.error.StripeError as e:
        flash(f'Error verifying payment: {str(e)}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/subscription/success')
def subscription_success():
    """
    Fallback route for subscription success (user redirect after checkout)
    
    NOTE: The primary handler is the webhook (customer.subscription.created).
    This route is a fallback for when users complete checkout and get redirected.
    The webhook is more reliable and should be the source of truth.
    """
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('No session ID provided', 'error')
        return redirect(url_for('index'))
    
    try:
        # Retrieve the checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get user from metadata
        user_id = checkout_session.metadata.get('user_id')
        payment_type = checkout_session.metadata.get('payment_type')
        
        if user_id and payment_type == 'subscription':
            # Subscription will be created via webhook, but we can show success message
            flash('Subscription successful! Your subscription is being activated.', 'success')
            return redirect(url_for('index'))
        
        flash('Subscription processing...', 'info')
        return redirect(url_for('index'))
        
    except stripe.error.StripeError as e:
        flash(f'Error verifying subscription: {str(e)}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

