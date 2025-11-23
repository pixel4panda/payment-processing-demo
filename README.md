# Payment Prototype Website

A Flask-based web application prototype that allows users to make one-time payments ($25) or subscribe monthly ($10/month). This project serves as a foundation for integrating real payment processing.

## Features

- **One-time payment option**: $25 single payment
- **Monthly subscription option**: $10/month recurring subscription
- **User dashboard**: View payment history and subscription status
- **SQLite database**: Simple file-based database for development

## Tech Stack

- **Backend**: Python 3.7+, Flask
- **Database**: SQLite (development)
- **Templates**: HTML, Jinja2
- **Styling**: CSS (inline)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)

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
- Supports multiple subscription tiers (plan_one, plan_two)
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
- `handle_subscription_updated()` - Updates subscription when plan/status changes
- `handle_subscription_deleted()` - Marks subscription as cancelled
- `handle_invoice_payment_succeeded()` - Updates subscription on successful renewal
- `handle_invoice_payment_failed()` - Updates subscription status when payment fails
- `handle_customer_updated()` - Updates customer information (name, email, etc.)
- `handle_payment_method_attached()` - Logs when a new payment method is attached to a customer

### **SECTION 5: SUCCESS ROUTES (Fallback for user redirects)**
- `/payment/success` - Fallback route for one-time payment redirects
- `/subscription/success` - Fallback route for subscription redirects
- **Note**: These are fallback routes for user experience. The webhook handlers (Section 3 & 4) are the primary source of truth for payment/subscription processing.

## Database Schema

- **users**: Stores user information (email, name, created_at)
- **payments**: Stores one-time payment records
- **subscriptions**: Stores subscription records with billing dates

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

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

The SQLite database (`instance/payment_prototype.db`) will be created automatically on first run.

## Next Steps: Stripe Integration

### Planned Integration Steps

1. **Install Stripe Python SDK**
   ```bash
   pip install stripe
   ```

2. **Set up Stripe account**
   - Create account at [stripe.com](https://stripe.com)
   - Get API keys (test and live)
   - Configure webhook endpoints

3. **Update payment flows**
   - Replace mock payment logic with Stripe Checkout or Payment Intents
   - Implement subscription creation with Stripe Subscriptions API
   - Add webhook handlers for payment events

4. **Environment variables**
   - Store Stripe API keys securely in environment variables
   - Use test keys for development, live keys for production

5. **Testing**
   - Use Stripe test mode and test cards
   - Test both one-time payments and subscription flows
   - Verify webhook handling
   
| Card Type | Number | CVC | Expiry |
| --- | --- | --- | --- |
| Visa | 4242 4242 4242 4242 | any 3 digits | any future date |
| Mastercard | 5555 5555 5555 4444 | any 3 digits | any future date |
| Amex | 3782 822463 10005 | any 4 digits | any future date |
| Decline Payment | 4000 0000 0000 0002 | any 3 digits | any future date |
   

### Stripe Resources

- **API Documentation**: https://docs.stripe.com/api
- **Python SDK**: https://stripe.com/docs/api/python
- **Checkout Session API**: https://stripe.com/docs/api/checkout/sessions
- **Subscriptions API**: https://stripe.com/docs/api/subscriptions
- **Webhooks Guide**: https://stripe.com/docs/webhooks
- **Test Cards**: https://stripe.com/docs/testing
- **Webhook Events Reference**: https://docs.stripe.com/api/events/types - **Complete list of all available webhook events**

## Webhook Events Reference

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



## Current Status

✅ **Completed**:
- Flask application structure
- Database models and schema
- HTML templates with modern UI
- Basic payment flow (mock implementation)
- User dashboard

🚧 **In Progress**:
- Stripe integration

## Important Notes

⚠️ **This is a prototype** - Current implementation uses mock payments. For production, you must:

- ✅ Integrate with Stripe 
- ✅ Implement proper authentication and session management
- ✅ Add HTTPS/SSL encryption
- ✅ Implement proper error handling and validation
- ✅ Set up proper extra security measures
- ✅ Add database migrations (Flask-Migrate)
- ✅ Implement proper logging and monitoring
- ✅ Add rate limiting and security headers

## License

This is a prototype project for demonstration purposes.

