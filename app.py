from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
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
    # -------END OFStripe incorporation-------
    return render_template('one_time_payment.html', 
                         stripe_publishable_key=stripe_publishable_key,
                         price_info=price_info)

@app.route('/payment/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        if not email or not name:
            flash('Please fill in all fields', 'error')
            return render_template('subscribe.html')
        
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
            flash('You already have an active subscription', 'info')
            return redirect(url_for('index'))
        
        # Create subscription (in production, integrate with payment gateway)
        subscription = Subscription(
            user_id=user.id,
            amount=10.00,
            status='active',
            start_date=datetime.utcnow(),
            next_billing_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(subscription)
        db.session.commit()
        
        flash('Subscription successful! You are now subscribed for $10/month.', 'success')
        return redirect(url_for('index'))
    
    return render_template('subscribe.html')

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

# Stripe required routes
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

@app.route('/payment/success')
def payment_success():
    """
    Handle successful payment completion (fallback route for embedded checkout)
    
    NOTE: With embedded checkout, payment completion is typically handled in-place.
    This route serves as a fallback if Stripe redirects here, or for webhook verification.
    In production, you should use webhooks to reliably track payment completion.
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

