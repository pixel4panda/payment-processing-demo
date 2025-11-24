# Payment Prototype Website

A Flask-based web application with full Stripe integration that allows users to make one-time payments or subscribe to monthly plans. This project demonstrates a complete payment processing implementation using Stripe's embedded checkout and webhook system.

## Features

- **One-time payments**: Secure payment processing using Stripe Checkout (embedded mode)
- **Subscription management**: Multiple subscription tiers with automatic billing
- **User dashboard**: View payment history and active subscriptions
- **Webhook integration**: Real-time event handling for payments and subscriptions
- **Fallback routes**: Redundant payment processing for reliability
- **SQLite database**: Simple file-based database for development (easily upgradeable to PostgreSQL/MySQL)

## Tech Stack

- **Backend**: Python 3.7+, Flask
- **Payment Processing**: Stripe API (Embedded Checkout)
- **Database**: SQLite (development) - SQLAlchemy ORM
- **Templates**: HTML, Jinja2
- **Styling**: CSS (inline)
- **Environment Management**: python-dotenv

## Payment Processor Decision: Stripe

After evaluating payment processors for a **Canadian-based business**, Stripe was selected as the payment processor of choice. Here's the reasoning:

#### 1. **Canadian Market Support**
- Native support for **CAD currency** transactions
- Compliant with Canadian financial regulations
- Established presence in the Canadian market

#### 2. **Developer-Friendly Integration**
- **Excellent API design**: API is intuitive to work with
- **Comprehensive documentation**: [Stripe API Documentation](https://docs.stripe.com/api) is among the best in the industry
- **Easy integration**: Well-maintained Python SDK (`stripe` package)
- **Testing tools**: Built-in test mode with test cards for development

#### 3. **Subscription & Recurring Payments**
- **Built-in subscription management**: Perfect for our $10/month recurring payment model
- **Automatic billing**: Handles subscription renewals, failed payments, and cancellations
- **Webhook support**: Real-time notifications for payment events

#### 4. **Security & Compliance**
- **PCI DSS compliant**: Stripe handles all sensitive payment data, reducing PCI compliance burden (Payment Card Industry Data Security Standard)
- **Built-in fraud prevention**: Advanced fraud detection and prevention tools
- **Secure by default**: Industry-standard encryption and security practices

#### 5. **Cost-Effective for Startups**
- **Transparent pricing**: 2.9% + $0.30 CAD per transaction (standard rate)
- **No setup fees**: No monthly fees or hidden costs for basic usage
- **Volume discounts**: Custom pricing packages available for high-volume businesses (contact sales)
- **Predictable costs**: Easy to calculate transaction costs

#### 6. **Additional Benefits**
- **Multiple payment methods**: Credit cards, debit cards, and digital wallets
- **Active community**: Large developer community and extensive resources

### Comparison with Alternatives

While other processors exist (PayPal, Square, Moneris, etc.), Stripe offers the best combination of:
- Ease of integration for developers
- Comprehensive subscription features
- Strong Canadian market presence
- Excellent documentation and support

## Project Structure

```
.
├── app.py                 # Main Flask application with routes
├── models.py              # Database models (User, Payment, Subscription)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── templates/
    ├── base.html         # Base template with common layout
    ├── index.html        # Home page with payment options
    ├── one_time_payment.html  # One-time payment form
    ├── subscribe.html    # Subscription form
    └── dashboard.html    # User dashboard
```

## Code Organization (app.py)

The Stripe integration in `app.py` is organized into clear sections:

### **SECTION 1: CHECKOUT SESSION - ONE-TIME PAYMENT**
- `/create-checkout-session` - Creates Stripe checkout session for one-time payments
- Returns `clientSecret` for embedded checkout

### **SECTION 2: CHECKOUT SESSION - SUBSCRIPTION**
- `/create-subscription-checkout-session` - Creates Stripe checkout session for subscriptions
- Supports multiple subscription tiers (Basic and Fancy plans)
- Returns `clientSecret` for embedded checkout

### **SECTION 3: WEBHOOK HANDLER**
- `/webhook` - Primary handler for all Stripe webhook events
- Handles the following events:
  - `checkout.session.completed` - One-time payment and subscription checkout completion
  - `customer.subscription.created` - Subscription successfully created for the first time
  - `customer.subscription.updated` - Subscription changed (upgrade/downgrade/status change)
  - `customer.subscription.deleted` - Subscription cancelled
  - `invoice.payment_succeeded` - Subscription renewed successfully
  - `invoice.payment_failed` - Subscription payment failed
  - `customer.updated` - Customer information changed (name, email, address, default payment method)
  - `payment_method.attached` - New payment method attached to customer

### **SECTION 4: WEBHOOK HANDLER FUNCTIONS**
- `handle_checkout_completed()` - Processes one-time payment success (creates Payment record)
- `handle_subscription_created()` - Creates subscription record when subscription is first created
  - Retrieves plan tier from metadata or checkout session
  - Handles date parsing from Unix timestamps
- `handle_subscription_updated()` - Updates subscription when plan/status changes
- `handle_subscription_deleted()` - Marks subscription as cancelled
- `handle_invoice_payment_succeeded()` - Updates subscription on successful renewal
- `handle_invoice_payment_failed()` - Updates subscription status when payment fails
- `handle_customer_updated()` - Updates customer information (name, email, etc.)
- `handle_payment_method_attached()` - Logs when a new payment method is attached to a customer

### **SECTION 5: FALLBACK ROUTES**
- `/payment/success` - Handles user redirect after one-time payment completion
- `/subscription/success` - Handles user redirect after subscription checkout completion
- Provides immediate user feedback while webhooks process in background

## Database Schema

### Users Table
- `id` (Integer, Primary Key)
- `email` (String, Unique, Not Null)
- `name` (String, Not Null)
- `created_at` (DateTime)

### Payments Table
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key → users.id)
- `amount` (Numeric)
- `payment_type` (String) - 'one_time' or 'subscription'
- `status` (String) - 'pending', 'completed', 'failed'
- `transaction_id` (String, Unique) - Stripe session/transaction ID
- `created_at` (DateTime)

### Subscriptions Table
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key → users.id)
- `amount` (Numeric)
- `status` (String) - 'active', 'cancelled', 'past_due', 'expired'
- `plan_tier` (String) - 'basic', 'fancy', etc.
- `stripe_subscription_id` (String, Unique) - Stripe subscription ID
- `stripe_price_id` (String) - Stripe price ID
- `start_date` (DateTime)
- `next_billing_date` (DateTime)
- `cancelled_at` (DateTime, Nullable)
- `created_at` (DateTime)

The database uses SQLAlchemy ORM, which provides:
- Type safety and validation
- Database-agnostic code (works with SQLite, PostgreSQL, MySQL, etc.)
- Automatic relationship management
- Easy migrations

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```env
   SECRET_KEY=your-secret-key-here
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
   STRIPE_PRICE_ID_ONE_TIME=price_your_one_time_price_id
   STRIPE_PRICE_ID_SUBS_ONE=price_your_basic_subscription_price_id
   STRIPE_PRICE_ID_SUBS_TWO=price_your_fancy_subscription_price_id
   DATABASE_URL=sqlite:///payment_prototype.db
   ```
   
   **Getting Stripe Keys:**
   - Create a Stripe account at [stripe.com](https://stripe.com)
   - Get your API keys from Dashboard → Developers → API keys
   - Create Products and Prices in Dashboard → Products
   - For local development, use Stripe CLI to forward webhooks:
     ```bash
     stripe listen --forward-to localhost:5000/webhook
     ```
     This will give you a webhook signing secret (starts with `whsec_`)

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

The SQLite database (`instance/payment_prototype.db`) will be created automatically on first run with the correct schema.

## Stripe Integration Details

### Implementation Overview

This application uses **Stripe Embedded Checkout** for a seamless payment experience. The checkout form is embedded directly in the page, keeping users on your site throughout the payment process.



### Key Integration Points

1. **Embedded Checkout**: Uses Stripe's `ui_mode='embedded'` for in-page checkout
2. **Webhook Processing**: Primary method for handling payment/subscription events
3. **Fallback Routes**: Secondary method for user redirects after checkout
4. **Metadata Tracking**: Uses Stripe metadata to link payments to users

### Testing with Stripe

Use Stripe's test mode and test cards for development:

| Card Type | Number | CVC | Expiry |
| --- | --- | --- | --- |
| Visa | 4242 4242 4242 4242 | any 3 digits | any future date |
| Mastercard | 5555 5555 5555 4444 | any 3 digits | any future date |
| Amex | 3782 822463 10005 | any 4 digits | any future date |
| Decline Payment | 4000 0000 0000 0002 | any 3 digits | any future date |

### Webhook Setup

**For Local Development:**
```bash
# Install Stripe CLI
# Then forward webhooks to your local server
stripe listen --forward-to localhost:5000/webhook
```

**For Production:**
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/webhook`
3. Select events to listen for (see webhook events section below)
4. Copy the signing secret to your `.env` file as `STRIPE_WEBHOOK_SECRET`
   

### Stripe Resources

- **API Documentation**: https://docs.stripe.com/api
- **Python SDK**: https://stripe.com/docs/api/python
- **Checkout Session API**: https://stripe.com/docs/api/checkout/sessions
- **Subscriptions API**: https://stripe.com/docs/api/subscriptions
- **Webhooks Guide**: https://stripe.com/docs/webhooks
- **Test Cards**: https://stripe.com/docs/testing
- **Webhook Events Reference**: https://docs.stripe.com/api/events/types - **Complete list of all available webhook events**


### Webhook explanation and decision process
A webhook is an automated message sent from one application to another (via an HTTP request), triggered by a specific event. They instantly deliver real-time data about an event, eliminating the need for one application to constantly "poll" another for updates.

      User A   triggers an event    on a    Source Application
      Source Application   sends   HTTP POST request    to    webhook URL
      Destination Application    listening at the URL,   receives    HTTP POST request
      Destination Application    performs action    

or

      ELI5
      Bob    buys a book    on a   Website
      Website    sends   letter with order    to    mail
      Bookstore     checking mail,    receives    letter with order
      Bookstore   gives book to Bob

You want a webhook whenever you need your server to automatically react to an event in real time. Examples:

- Payment succeeded / failed
- Subscription renewed / canceled
- Inventory updated in a 3rd-party service

IMPORTANT: Webhook endpoints either have a specific API version set or use the default API version of the Stripe account. If you use any of the supported static language SDKs (.NET, Java or Go) to process events, the API version set for webhooks should match the version used to generate the SDKs. 

*Example: if you are using Python, check the documentation. As of 251123 it states Python 3.6 or newer required.*

**Where to find all available events**: The complete list of all Stripe webhook events is available at: https://docs.stripe.com/api/events/types

This application currently handles the following webhook events:

### Payment & Checkout Events

#### `checkout.session.completed`
- **When it fires**: After a customer successfully completes a checkout session
- **What it handles**: 
  - One-time payment success (creates Payment record in database)
  - Initial subscription checkout completion (subscription creation handled separately via `customer.subscription.created`)
- **Handler function**: `handle_checkout_completed()`

### Subscription Events

#### `customer.subscription.created`
- **When it fires**: When a subscription is successfully created for the first time
- **What it handles**: Creates subscription record in database with plan tier, amount, and billing dates
- **Handler function**: `handle_subscription_created()`

#### `customer.subscription.updated`
- **When it fires**: When subscription properties change
- **What it handles**: 
  - Plan tier changes (upgrade/downgrade)
  - Subscription status changes (active → past_due, etc.)
  - Billing cycle changes
  - Subscription amount changes
- **Handler function**: `handle_subscription_updated()`
- **Note**: This does NOT fire for customer info changes (name, address) - see `customer.updated`

#### `customer.subscription.deleted`
- **When it fires**: When a subscription is cancelled
- **What it handles**: Marks subscription as cancelled and records cancellation date
- **Handler function**: `handle_subscription_deleted()`

### Invoice Events

#### `invoice.payment_succeeded`
- **When it fires**: When a subscription invoice payment succeeds (renewal)
- **What it handles**: Updates subscription's next billing date and ensures status is active
- **Handler function**: `handle_invoice_payment_succeeded()`

#### `invoice.payment_failed`
- **When it fires**: When a subscription invoice payment fails
- **What it handles**: Updates subscription status to 'past_due'
- **Handler function**: `handle_invoice_payment_failed()`

### Customer Events

#### `customer.updated`
- **When it fires**: When customer object properties change
- **What it handles**: 
  - Name changes
  - Email changes
  - Address changes (when implemented)
  - Phone number changes (when implemented)
  - Default payment method changes
  - Customer metadata changes
- **Handler function**: `handle_customer_updated()`
- **Important**: This is different from `customer.subscription.updated` - that handles subscription changes, this handles customer profile changes

### Payment Method Events

#### `payment_method.attached`
- **When it fires**: When a payment method is attached to a customer
- **What it handles**: 
  - New payment method added to customer
  - Logs the attachment event
  - Identifies if it's the default payment method
- **Handler function**: `handle_payment_method_attached()`
- **Difference from `setup_intent.succeeded`**: 
  - `payment_method.attached` fires when a payment method is attached to a customer
  - `setup_intent.succeeded` fires when a SetupIntent succeeds (used to set up payment methods for future use)
  - Both can occur, but `payment_method.attached` is more direct for tracking when a customer adds a payment method

### Event Differences Explained

**`customer.updated` vs `customer.subscription.updated`**:
- `customer.updated` = Customer profile changes (name, email, address, default payment method)
- `customer.subscription.updated` = Subscription changes (plan, status, billing cycle)

**`payment_method.attached` vs `setup_intent.succeeded`**:
- `payment_method.attached` = Payment method successfully attached to customer (direct event)
- `setup_intent.succeeded` = SetupIntent completed (indirect - may or may not result in attachment)
- **Recommendation**: Use `payment_method.attached` for tracking when customers add payment methods

**`customer.updated` for payment method changes**:
- When a customer's default payment method changes, `customer.updated` fires
- The `invoice_settings.default_payment_method` field in the customer object will reflect the new default
- You can also listen to `payment_method.attached` to know when new methods are added

## Fallback Routes (Recommended)

While webhooks are the **primary and most reliable** method for processing payments and subscriptions, implementing fallback routes is **highly recommended** for production applications. These routes handle user redirects after checkout completion.

### Why Fallback Routes Are Recommended

1. **Webhook Reliability Issues**
   - Webhooks can be delayed due to network issues, server downtime, or Stripe's retry mechanisms
   - In rare cases, webhooks may fail to deliver (though Stripe retries up to 3 days)
   - Your server might be temporarily unavailable when the webhook fires

2. **Immediate User Feedback**
   - Users expect immediate confirmation after completing payment
   - Fallback routes provide instant feedback while webhooks process in the background
   - Improves user experience and reduces support inquiries

3. **Redundancy and Data Integrity**
   - Acts as a safety net if webhook processing fails
   - Prevents lost payment records due to webhook delivery failures
   - Ensures critical payment data is captured even if webhooks are delayed

4. **Development and Testing**
   - Easier to test payment flows during development
   - Useful for debugging when webhook delivery is problematic
   - Provides a way to verify payments without waiting for webhooks

### What Fallback Routes Should Contain

Fallback routes should be implemented for both one-time payments and subscriptions. Here's what each should include:

#### `/payment/success` (One-Time Payment Fallback)

**Required Functionality:**
1. **Extract session ID** from URL query parameter (`?session_id=cs_test_...`)
   - Stripe automatically appends this when redirecting after checkout
   - The `{CHECKOUT_SESSION_ID}` placeholder in `return_url` gets replaced by Stripe

2. **Retrieve checkout session from Stripe**
   - Use `stripe.checkout.Session.retrieve(session_id)` to verify the payment
   - This ensures the session is valid and payment was actually completed

3. **Check for duplicate records** (idempotency)
   - Query database to see if payment was already recorded by webhook
   - Prevents duplicate payment records if both webhook and fallback route process the same payment

4. **Create payment record if missing**
   - Only create record if webhook hasn't already processed it
   - Extract amount from checkout session (convert from cents to dollars)
   - Use session ID as transaction ID for tracking

5. **User feedback**
   - Display success message to user
   - Redirect to appropriate page (dashboard, home, etc.)

**Example Implementation Pattern:**
```python
@app.route('/payment/success')
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('No session ID provided', 'error')
        return redirect(url_for('index'))
    
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        user_id = checkout_session.metadata.get('user_id')
        payment_type = checkout_session.metadata.get('payment_type')
        
        if user_id and payment_type == 'one_time':
            user = User.query.get(int(user_id))
            if user:
                # Check if already processed by webhook
                existing_payment = Payment.query.filter_by(
                    user_id=user.id,
                    transaction_id=session_id
                ).first()
                
                if not existing_payment:
                    # Create payment record as fallback
                    amount = checkout_session.amount_total / 100
                    payment = Payment(
                        user_id=user.id,
                        amount=amount,
                        payment_type='one_time',
                        status='completed',
                        transaction_id=session_id
                    )
                    db.session.add(payment)
                    db.session.commit()
        
        flash('Payment successful!', 'success')
        return redirect(url_for('dashboard', email=user.email))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))
```

#### `/subscription/success` (Subscription Fallback)

**Required Functionality:**
1. **Extract session ID** from URL query parameter
2. **Retrieve checkout session from Stripe** to verify subscription checkout
3. **Display success message** (subscription creation is handled by webhook)
4. **Optional: Check subscription status** if you want to show immediate confirmation
   - Note: Subscription may not be fully created yet if webhook is delayed
   - Best practice: Show "processing" message and redirect to dashboard

**Example Implementation Pattern:**
```python
@app.route('/subscription/success')
def subscription_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('No session ID provided', 'error')
        return redirect(url_for('index'))
    
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        user_id = checkout_session.metadata.get('user_id')
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                # Subscription will be created via webhook
                # Show success message and redirect
                flash('Subscription successful! Your subscription is being activated.', 'success')
                return redirect(url_for('dashboard', email=user.email))
        
        flash('Subscription processing...', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))
```

### Important Considerations

1. **Webhooks are Primary**: Always treat webhooks as the source of truth. Fallback routes should only create records if they don't already exist.

2. **Double check**: Always check for existing records before creating new ones to prevent duplicates.

3. **Error Handling**: Implement proper error handling for Stripe API calls and database operations.

4. **Security**: Verify the session ID is valid by retrieving it from Stripe. Don't trust user input alone.

5. **User Experience**: Provide clear feedback to users, even if the webhook hasn't processed yet.

6. **Return URL Configuration**: In your checkout session creation, set `return_url` to point to these fallback routes:
   ```python
   return_url=base_url + '/payment/success?session_id={CHECKOUT_SESSION_ID}'
   ```

### When to Use Fallback Routes

- ✅ **Production applications**: Always implement for redundancy
- ✅ **User-facing applications**: Essential for good UX
- ✅ **Critical payment flows**: When payment records must be captured reliably
- ⚠️ **Development**: Can be helpful for testing, but webhooks are still primary

### When Fallback Routes May Not Be Necessary

- ⚠️ **Internal tools**: If only internal users and webhook reliability is acceptable
- ⚠️ **Non-critical payments**: If occasional missed payments are acceptable


## Current Status

✅ **Completed**:
- Flask application structure with full Stripe integration
- Database models and schema with all required fields
- HTML templates with modern UI
- Stripe Embedded Checkout for one-time payments
- Stripe Embedded Checkout for subscriptions (multiple tiers)
- Complete webhook handler system (8 event types)
- Fallback routes for payment/subscription success
- User dashboard with payment history and subscription management
- Error handling and logging
- Environment variable configuration

## Production Considerations

⚠️ **This is a prototype** - For production deployment, consider:

- ✅ **Authentication**: Implement proper user authentication and session management
- ✅ **HTTPS/SSL**: Always use HTTPS in production (Stripe requires it)
- ✅ **Database**: Consider upgrading from SQLite to PostgreSQL or MySQL
- ✅ **Logging**: Implement proper logging system (e.g., Python logging module)
- ✅ **Monitoring**: Set up error tracking (e.g., Sentry) and monitoring
- ✅ **Rate Limiting**: Add rate limiting to prevent abuse
- ✅ **Security Headers**: Implement security headers (CSP, HSTS, etc.)
- ✅ **Environment Variables**: Use secure secret management (AWS Secrets Manager, etc.)
- ✅ **Testing**: Add comprehensive unit and integration tests

## License

This is a prototype project for demonstration purposes.

