import stripe
import paypalrestsdk
import uuid
from datetime import datetime, timedelta
from typing import Dict
import mysql.connector
import os

class PaymentProcessor:
    """Production Payment Processor"""
    
    def __init__(self):
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        paypalrestsdk.configure({
            'mode': os.getenv('PAYPAL_MODE', 'sandbox'),
            'client_id': os.getenv('PAYPAL_CLIENT_ID', ''),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET', '')
        })
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'tera_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'tera_engine')
        }
        
        self.plans = {
            'monthly': {'price': float(os.getenv('MONTHLY_PRICE', 29.99)), 'period': 30},
            'annual': {'price': float(os.getenv('ANNUAL_PRICE', 299.99)), 'period': 365},
            'pro': {'price': 0.00, 'period': 36500}
        }
    
    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def create_stripe_subscription(self, user_id: str, plan_type: str, payment_method_id: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            if not user['stripe_customer_id']:
                customer = stripe.Customer.create(email=user['email'], payment_method=payment_method_id, invoice_settings={'default_payment_method': payment_method_id})
                cursor.execute("UPDATE users SET stripe_customer_id = %s WHERE id = %s", (customer.id, user_id))
                conn.commit()
            else:
                customer = stripe.Customer.retrieve(user['stripe_customer_id'])
            
            plan = self.plans[plan_type]
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f'TERA {plan_type.title()} Subscription'}, 'unit_amount': int(plan['price'] * 100), 'recurring': {'interval': 'month' if plan_type == 'monthly' else 'year'}}}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            
            sub_id = str(uuid.uuid4())
            start_date = datetime.now()
            end_date = start_date + timedelta(days=plan['period'])
            
            cursor.execute("""
                INSERT INTO subscriptions (id, user_id, plan_type, price, status, payment_method, payment_id, start_date, end_date)
                VALUES (%s, %s, %s, %s, 'active', 'stripe', %s, %s, %s)
            """, (sub_id, user_id, plan_type, plan['price'], subscription.id, start_date, end_date))
            
            limits = {'monthly': {'gen': 1000, 'dl': 1000, 'st': 100, 'api': 10000}, 'annual': {'gen': 20000, 'dl': 20000, 'st': 1000, 'api': 200000}, 'pro': {'gen': -1, 'dl': -1, 'st': -1, 'api': -1}}[plan_type]
            
            cursor.execute("""
                UPDATE users SET subscription_tier = %s, subscription_status = 'active', subscription_start = %s, subscription_end = %s WHERE id = %s
            """, (plan_type, start_date, end_date, user_id))
            
            cursor.execute("""
                UPDATE usage_limits SET subscription_tier = %s, generations_limit = %s, downloads_limit = %s, storage_limit_gb = %s, api_calls_limit = %s WHERE user_id = %s
            """, (plan_type, limits['gen'], limits['dl'], limits['st'], limits['api'], user_id))
            
            conn.commit()
            return {'success': True, 'subscription_id': sub_id, 'client_secret': subscription.latest_invoice.payment_intent.client_secret}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def pay_per_use(self, user_id: str, item_type: str, item_id: str, price: float) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            payment_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO pay_per_use (id, user_id, item_type, item_id, price, payment_status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """, (payment_id, user_id, item_type, item_id, price))
            conn.commit()
            
            intent = stripe.PaymentIntent.create(amount=int(price * 100), currency='usd', metadata={'payment_id': payment_id, 'user_id': user_id})
            return {'success': True, 'client_secret': intent.client_secret, 'payment_id': payment_id}
        finally:
            cursor.close()
            conn.close()
