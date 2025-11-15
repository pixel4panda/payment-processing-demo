from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import os

# Import db from models to avoid circular import
from models import db, User, Payment, Subscription

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///payment_prototype.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment/one-time', methods=['GET', 'POST'])
def one_time_payment():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        if not email or not name:
            flash('Please fill in all fields', 'error')
            return render_template('one_time_payment.html')
        
        # Check if user exists, create if not
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
        
        # Check if user already has a one-time payment
        existing_payment = Payment.query.filter_by(user_id=user.id, payment_type='one_time').first()
        if existing_payment:
            flash('You have already made a one-time payment', 'info')
            return redirect(url_for('index'))
        
        # Create payment record (in production, integrate with payment gateway)
        payment = Payment(
            user_id=user.id,
            amount=25.00,
            payment_type='one_time',
            status='completed'  # In production, this would be 'pending' until payment gateway confirms
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('Payment successful! Thank you for your $25 one-time payment.', 'success')
        return redirect(url_for('index'))
    
    return render_template('one_time_payment.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

