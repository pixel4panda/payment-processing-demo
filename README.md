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

- ✅ Integrate with Stripe (or another payment processor)
- ✅ Implement proper authentication and session management
- ✅ Add HTTPS/SSL encryption
- ✅ Implement proper error handling and validation
- ✅ Add payment webhooks for subscription renewals
- ✅ Set up proper security measures
- ✅ Use environment variables for sensitive data (API keys)
- ✅ Add database migrations (Flask-Migrate)
- ✅ Implement proper logging and monitoring
- ✅ Add rate limiting and security headers

## License

This is a prototype project for demonstration purposes.

