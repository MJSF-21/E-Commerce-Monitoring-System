from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from functools import wraps
from datetime import datetime, timedelta
import json
import random
import os
from dotenv import load_dotenv
import bcrypt
import jwt
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-ecommerce-2024')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Database Configuration
DATABASE_FILE = 'ecommerce_database.json'

class DatabaseManager:
    def __init__(self):
        self.data_file = DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        if not os.path.exists(self.data_file):
            self.create_sample_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return self.get_empty_schema()
    
    def save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_empty_schema(self):
        return {
            'users': [],
            'products': [],
            'categories': [],
            'sales': [],
            'customers': [],
            'customer_profiles': [],
            'shopping_carts': [],
            'wishlists': [],
            'customer_reviews': [],
            'loyalty_programs': [],
            'support_tickets': [],
            'inventory_transactions': [],
            'audit_logs': [],
            'settings': {
                'store_name': 'E-Commerce Store',
                'currency': 'USD',
                'tax_rate': 0.08,
                'low_stock_threshold': 10,
                'loyalty_points_per_dollar': 1,
                'welcome_bonus_points': 100
            }
        }
    
    def create_sample_data(self):
        data = self.get_empty_schema()
        
        # Categories
        data['categories'] = [
            {'id': 1, 'name': 'Electronics', 'description': 'Electronic devices and accessories', 'created_at': datetime.now().isoformat()},
            {'id': 2, 'name': 'Furniture', 'description': 'Office and home furniture', 'created_at': datetime.now().isoformat()},
            {'id': 3, 'name': 'Office Supplies', 'description': 'Stationery and office items', 'created_at': datetime.now().isoformat()},
            {'id': 4, 'name': 'Accessories', 'description': 'Computer and mobile accessories', 'created_at': datetime.now().isoformat()},
            {'id': 5, 'name': 'Software', 'description': 'Digital products and licenses', 'created_at': datetime.now().isoformat()}
        ]
        
        # Users with different roles
        data['users'] = [
            {'id': 1, 'username': 'admin', 'email': 'admin@ecommerce.com', 'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'role': 'admin', 'full_name': 'System Administrator', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 2, 'username': 'cashier', 'email': 'cashier@ecommerce.com', 'password': bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'role': 'cashier', 'full_name': 'Cashier User', 'active': True, 'created_at': datetime.now().isoformat()}
        ]
        
        # Customer profiles (for registered customers)
        data['customer_profiles'] = []
        
        # Shopping carts (for active sessions)
        data['shopping_carts'] = []
        
        # Wishlists (customer saved items)
        data['wishlists'] = []
        
        # Customer reviews and ratings
        data['customer_reviews'] = [
            {'id': 1, 'customer_id': 1, 'product_id': 1, 'rating': 5, 'review': 'Excellent laptop! Very fast and reliable.', 'created_at': datetime.now().isoformat()},
            {'id': 2, 'customer_id': 2, 'product_id': 2, 'rating': 4, 'review': 'Good mouse, comfortable to use.', 'created_at': datetime.now().isoformat()}
        ]
        
        # Loyalty programs
        data['loyalty_programs'] = [
            {'id': 1, 'name': 'Bronze', 'points_required': 0, 'discount_percent': 0, 'benefits': ['Basic rewards']},
            {'id': 2, 'name': 'Silver', 'points_required': 500, 'discount_percent': 5, 'benefits': ['5% discount', 'Free shipping on orders over $50']},
            {'id': 3, 'name': 'Gold', 'points_required': 1000, 'discount_percent': 10, 'benefits': ['10% discount', 'Free shipping', 'Early access to sales']},
            {'id': 4, 'name': 'Platinum', 'points_required': 2500, 'discount_percent': 15, 'benefits': ['15% discount', 'Free shipping', 'Early access', 'Exclusive products']}
        ]
        
        # Support tickets
        data['support_tickets'] = []
        
        # Products with comprehensive details
        data['products'] = [
            {'id': 1, 'name': 'Laptop Pro 15"', 'sku': 'LP-001', 'barcode': '123456789001', 'price': 999.99, 'cost': 750.00, 'stock': 15, 'min_stock': 5, 'category_id': 1, 'supplier': 'TechSupplier Inc', 'description': 'High-performance laptop with 16GB RAM and 512GB SSD', 'weight': 2.5, 'dimensions': '35.5 x 23.5 x 1.8 cm', 'warranty': '2 years', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 2, 'name': 'Wireless Mouse', 'sku': 'WM-002', 'barcode': '123456789002', 'price': 25.99, 'cost': 15.00, 'stock': 50, 'min_stock': 10, 'category_id': 1, 'supplier': 'TechSupplier Inc', 'description': 'Ergonomic wireless mouse with precision tracking', 'weight': 0.1, 'dimensions': '10 x 6 x 3.5 cm', 'warranty': '1 year', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 3, 'name': 'Mechanical Keyboard', 'sku': 'KB-003', 'barcode': '123456789003', 'price': 79.99, 'cost': 45.00, 'stock': 30, 'min_stock': 8, 'category_id': 1, 'supplier': 'Peripheral Co', 'description': 'RGB mechanical keyboard with blue switches', 'weight': 0.8, 'dimensions': '44 x 13 x 4 cm', 'warranty': '1 year', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 4, 'name': '4K Monitor 27"', 'sku': 'MN-004', 'barcode': '123456789004', 'price': 299.99, 'cost': 200.00, 'stock': 20, 'min_stock': 5, 'category_id': 1, 'supplier': 'DisplayTech', 'description': '4K UHD monitor with HDR support', 'weight': 5.2, 'dimensions': '61 x 36 x 20 cm', 'warranty': '3 years', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 5, 'name': 'Executive Desk Chair', 'sku': 'DC-005', 'barcode': '123456789005', 'price': 199.99, 'cost': 120.00, 'stock': 10, 'min_stock': 3, 'category_id': 2, 'supplier': 'FurniturePlus', 'description': 'Ergonomic office chair with lumbar support', 'weight': 15.0, 'dimensions': '65 x 65 x 120 cm', 'warranty': '5 years', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 6, 'name': 'LED Desk Lamp', 'sku': 'DL-006', 'barcode': '123456789006', 'price': 39.99, 'cost': 25.00, 'stock': 25, 'min_stock': 8, 'category_id': 2, 'supplier': 'FurniturePlus', 'description': 'Adjustable LED lamp with touch controls', 'weight': 1.2, 'dimensions': '15 x 15 x 45 cm', 'warranty': '2 years', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 7, 'name': 'Premium Notebook Set', 'sku': 'NB-007', 'barcode': '123456789007', 'price': 9.99, 'cost': 5.00, 'stock': 100, 'min_stock': 20, 'category_id': 3, 'supplier': 'Office Supplies Co', 'description': 'Set of 5 premium A4 notebooks', 'weight': 0.5, 'dimensions': '21 x 29.7 x 2 cm', 'warranty': 'N/A', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 8, 'name': 'Executive Pen Set', 'sku': 'PS-008', 'barcode': '123456789008', 'price': 14.99, 'cost': 8.00, 'stock': 75, 'min_stock': 15, 'category_id': 3, 'supplier': 'Office Supplies Co', 'description': 'Luxury ballpoint pen set with gift box', 'weight': 0.3, 'dimensions': '20 x 10 x 3 cm', 'warranty': '1 year', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 9, 'name': 'USB-C Hub 7-in-1', 'sku': 'UH-009', 'barcode': '123456789009', 'price': 49.99, 'cost': 30.00, 'stock': 40, 'min_stock': 10, 'category_id': 4, 'supplier': 'TechSupplier Inc', 'description': '7-in-1 USB-C hub with HDMI and SD card reader', 'weight': 0.05, 'dimensions': '12 x 4 x 1.5 cm', 'warranty': '1 year', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 10, 'name': 'Phone Stand Adjustable', 'sku': 'PH-010', 'barcode': '123456789010', 'price': 19.99, 'cost': 12.00, 'stock': 60, 'min_stock': 12, 'category_id': 4, 'supplier': 'Accessory World', 'description': 'Adjustable phone stand for all devices', 'weight': 0.2, 'dimensions': '8 x 8 x 12 cm', 'warranty': '6 months', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 11, 'name': 'Office Suite Pro', 'sku': 'SW-011', 'barcode': '123456789011', 'price': 149.99, 'cost': 50.00, 'stock': 999, 'min_stock': 100, 'category_id': 5, 'supplier': 'Software Corp', 'description': 'Professional office suite license (1 year)', 'weight': 0, 'dimensions': 'Digital', 'warranty': '1 year support', 'active': True, 'created_at': datetime.now().isoformat()},
            {'id': 12, 'name': 'Antivirus Premium', 'sku': 'SW-012', 'barcode': '123456789012', 'price': 79.99, 'cost': 25.00, 'stock': 999, 'min_stock': 50, 'category_id': 5, 'supplier': 'Security Software Inc', 'description': 'Premium antivirus protection (3 devices)', 'weight': 0, 'dimensions': 'Digital', 'warranty': '1 year updates', 'active': True, 'created_at': datetime.now().isoformat()}
        ]
        
        # Customers with detailed information
        data['customers'] = [
            {'id': 1, 'name': 'John Smith', 'email': 'john.smith@email.com', 'phone': '+1-555-0101', 'address': '123 Main Street', 'city': 'New York', 'state': 'NY', 'zip': '10001', 'country': 'USA', 'company': 'ABC Corporation', 'customer_type': 'business', 'credit_limit': 5000.00, 'created_at': datetime.now().isoformat()},
            {'id': 2, 'name': 'Sarah Johnson', 'email': 'sarah.j@email.com', 'phone': '+1-555-0102', 'address': '456 Oak Avenue', 'city': 'Los Angeles', 'state': 'CA', 'zip': '90210', 'country': 'USA', 'company': 'Individual', 'customer_type': 'individual', 'credit_limit': 1000.00, 'created_at': datetime.now().isoformat()},
            {'id': 3, 'name': 'Mike Wilson', 'email': 'mike.wilson@email.com', 'phone': '+1-555-0103', 'address': '789 Pine Road', 'city': 'Chicago', 'state': 'IL', 'zip': '60601', 'country': 'USA', 'company': 'XYZ Enterprises', 'customer_type': 'business', 'credit_limit': 10000.00, 'created_at': datetime.now().isoformat()},
            {'id': 4, 'name': 'Emily Davis', 'email': 'emily.d@email.com', 'phone': '+1-555-0104', 'address': '321 Elm Street', 'city': 'Houston', 'state': 'TX', 'zip': '77001', 'country': 'USA', 'company': 'Individual', 'customer_type': 'individual', 'credit_limit': 500.00, 'created_at': datetime.now().isoformat()},
            {'id': 5, 'name': 'Robert Brown', 'email': 'robert.brown@email.com', 'phone': '+1-555-0105', 'address': '654 Maple Drive', 'city': 'Phoenix', 'state': 'AZ', 'zip': '85001', 'country': 'USA', 'company': 'Global Solutions Inc', 'customer_type': 'business', 'credit_limit': 15000.00, 'created_at': datetime.now().isoformat()}
        ]
        
        # Sales with comprehensive details
        data['sales'] = []
        for i in range(50):
            sale = {
                'id': i + 1,
                'sale_number': f'SALE-{str(i+1).zfill(4)}',
                'customer_id': random.choice([c['id'] for c in data['customers']]),
                'user_id': random.choice([u['id'] for u in data['users']]),
                'items': [],
                'subtotal': 0,
                'tax': 0,
                'total': 0,
                'discount': 0,
                'payment_method': random.choice(['cash', 'card', 'transfer', 'credit']),
                'status': random.choice(['completed', 'pending', 'cancelled']) if i < 5 else 'completed',
                'sale_date': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
                'notes': f'Transaction notes for sale #{i+1}',
                'invoice_number': f'INV-{str(i+1).zfill(4)}',
                'shipping_address': None,
                'billing_address': None
            }
            
            # Add random items to sale
            num_items = random.randint(1, 5)
            for j in range(num_items):
                product = random.choice(data['products'])
                quantity = random.randint(1, 3)
                item = {
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'sku': product['sku'],
                    'quantity': quantity,
                    'unit_price': product['price'],
                    'discount': 0,
                    'total_price': product['price'] * quantity
                }
                sale['items'].append(item)
                sale['subtotal'] += item['total_price']
            
            # Apply random discount
            if random.random() > 0.7:
                sale['discount'] = sale['subtotal'] * 0.1  # 10% discount
                sale['subtotal'] -= sale['discount']
            
            sale['tax'] = sale['subtotal'] * data['settings']['tax_rate']
            sale['total'] = sale['subtotal'] + sale['tax']
            data['sales'].append(sale)
        
        # Inventory transactions
        data['inventory_transactions'] = []
        transaction_id = 1
        
        # Initial stock transactions
        for product in data['products']:
            data['inventory_transactions'].append({
                'id': transaction_id,
                'product_id': product['id'],
                'transaction_type': 'initial',
                'quantity': product['stock'],
                'reference': 'Initial Stock Setup',
                'user_id': 1,
                'timestamp': datetime.now().isoformat(),
                'notes': f'Initial stock for {product["name"]}'
            })
            transaction_id += 1
        
        # Sample inventory adjustments
        for i in range(20):
            product = random.choice(data['products'])
            adjustment = random.randint(-5, 10)
            data['inventory_transactions'].append({
                'id': transaction_id,
                'product_id': product['id'],
                'transaction_type': 'adjustment',
                'quantity': adjustment,
                'reference': f'Stock Adjustment #{i+1}',
                'user_id': random.choice([u['id'] for u in data['users']]),
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'notes': f'Inventory adjustment for {product["name"]}'
            })
            transaction_id += 1
        
        # Audit logs
        data['audit_logs'] = [
            {'id': 1, 'user_id': 1, 'action': 'system_initialized', 'table': 'system', 'record_id': None, 'old_values': None, 'new_values': None, 'timestamp': datetime.now().isoformat(), 'ip_address': '127.0.0.1'},
            {'id': 2, 'user_id': 1, 'action': 'data_import', 'table': 'products', 'record_id': None, 'old_values': None, 'new_values': {'count': len(data['products'])}, 'timestamp': datetime.now().isoformat(), 'ip_address': '127.0.0.1'}
        ]
        
        self.save_data(data)

# Initialize database
db = DatabaseManager()

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            data = db.load_data()
            user = next((u for u in data['users'] if u['id'] == session['user_id']), None)
            if not user or user['role'] not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        data = db.load_data()
        user = next((u for u in data['users'] if u['username'] == username and u['active']), None)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            # Log the login
            data['audit_logs'].append({
                'id': len(data['audit_logs']) + 1,
                'user_id': user['id'],
                'action': 'login',
                'table': 'users',
                'record_id': user['id'],
                'old_values': None,
                'new_values': {'login_time': datetime.now().isoformat()},
                'timestamp': datetime.now().isoformat(),
                'ip_address': request.remote_addr
            })
            db.save_data(data)
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        data = db.load_data()
        data['audit_logs'].append({
            'id': len(data['audit_logs']) + 1,
            'user_id': session['user_id'],
            'action': 'logout',
            'table': 'users',
            'record_id': session['user_id'],
            'old_values': None,
            'new_values': {'logout_time': datetime.now().isoformat()},
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        })
        db.save_data(data)
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        data = db.load_data()
        
        # Check if username or email already exists
        if any(u['username'] == username for u in data['users']):
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if any(u['email'] == email for u in data['users']):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new customer user
        new_user_id = max([u['id'] for u in data['users']], default=0) + 1
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        new_user = {
            'id': new_user_id,
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': 'customer',
            'full_name': full_name,
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        data['users'].append(new_user)
        
        # Create customer profile
        customer_profile = {
            'id': new_user_id,
            'user_id': new_user_id,
            'phone': phone,
            'address': '',
            'city': '',
            'state': '',
            'zip_code': '',
            'country': '',
            'loyalty_points': data['settings'].get('welcome_bonus_points', 100),
            'loyalty_tier': 'Bronze',
            'total_orders': 0,
            'total_spent': 0.0,
            'wishlist_count': 0,
            'email_notifications': True,
            'sms_notifications': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Ensure customer profiles table exists
        if 'customer_profiles' not in data:
            data['customer_profiles'] = []
        data['customer_profiles'].append(customer_profile)
        
        # Ensure shopping carts table exists
        if 'shopping_carts' not in data:
            data['shopping_carts'] = []
        
        # Create empty shopping cart for the customer
        shopping_cart = {
            'id': new_user_id,
            'customer_id': new_user_id,
            'items': [],
            'total': 0.0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['shopping_carts'].append(shopping_cart)
        
        # Ensure wishlists table exists
        if 'wishlists' not in data:
            data['wishlists'] = []
        
        # Create empty wishlist for the customer
        wishlist = {
            'id': new_user_id,
            'customer_id': new_user_id,
            'items': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['wishlists'].append(wishlist)
        
        # Log the registration
        data['audit_logs'].append({
            'id': len(data['audit_logs']) + 1,
            'user_id': new_user_id,
            'action': 'register',
            'table': 'users',
            'record_id': new_user_id,
            'old_values': None,
            'new_values': {'username': username, 'email': email, 'role': 'customer'},
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        })
        
        db.save_data(data)
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Main Routes
@app.route('/')
@login_required
def dashboard():
    if session['role'] == 'customer':
        return redirect(url_for('customer_dashboard'))
    
    data = db.load_data()
    stats = get_dashboard_stats(data)
    return render_template('index.html', stats=stats)

@app.route('/admin')
@login_required
@role_required('admin')
def admin():
    return render_template('admin.html')

@app.route('/store')
@login_required
@role_required('admin', 'cashier')
def store():
    return render_template('store.html')

@app.route('/customer')
@login_required
@role_required('customer')
def customer_dashboard():
    data = db.load_data()
    user_id = session['user_id']
    
    # Ensure customer system tables exist
    if 'customer_profiles' not in data:
        data['customer_profiles'] = []
    if 'shopping_carts' not in data:
        data['shopping_carts'] = []
    if 'wishlists' not in data:
        data['wishlists'] = []
    if 'customer_reviews' not in data:
        data['customer_reviews'] = []
    if 'support_tickets' not in data:
        data['support_tickets'] = []
    
    # Get customer profile
    customer_profile = next((cp for cp in data['customer_profiles'] if cp['user_id'] == user_id), None)
    
    # Get customer's orders
    customer_orders = [s for s in data['sales'] if s.get('customer_id') == user_id]
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    # Get customer's wishlist
    wishlist = next((w for w in data['wishlists'] if w['customer_id'] == user_id), None)
    
    # Calculate customer statistics
    total_orders = len(customer_orders)
    total_spent = sum(s['total'] for s in customer_orders)
    total_items = sum(len(s['items']) for s in customer_orders)
    
    # Get customer's reviews
    customer_reviews = [r for r in data['customer_reviews'] if r['customer_id'] == user_id]
    
    # Get customer's support tickets
    support_tickets = [t for t in data['support_tickets'] if t['customer_id'] == user_id]
    
    customer_stats = {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'total_items': total_items,
        'loyalty_points': customer_profile['loyalty_points'] if customer_profile else 0,
        'loyalty_tier': customer_profile['loyalty_tier'] if customer_profile else 'Bronze',
        'cart_items': len(shopping_cart['items']) if shopping_cart else 0,
        'wishlist_items': len(wishlist['items']) if wishlist else 0,
        'reviews_count': len(customer_reviews),
        'support_tickets_count': len(support_tickets)
    }
    
    return render_template('customer_dashboard.html', 
                         customer_stats=customer_stats,
                         customer_profile=customer_profile,
                         customer_orders=customer_orders,
                         shopping_cart=shopping_cart,
                         wishlist=wishlist,
                         customer_reviews=customer_reviews,
                         support_tickets=support_tickets)

@app.route('/customer/store')
@login_required
@role_required('customer')
def customer_store():
    return render_template('customer_store.html')

@app.route('/analytics')
@login_required
@role_required('admin')
def analytics():
    return render_template('analytics.html')

# API Routes
@app.route('/api/dashboard/stats')
@login_required
def get_dashboard_stats_api():
    data = db.load_data()
    return jsonify(get_dashboard_stats(data))

def get_dashboard_stats(data):
    today = datetime.now().date()
    today_sales = [s for s in data['sales'] if datetime.fromisoformat(s['sale_date']).date() == today]
    this_month = [s for s in data['sales'] if datetime.fromisoformat(s['sale_date']).month == today.month]
    
    return {
        'total_products': len([p for p in data['products'] if p['active']]),
        'total_categories': len(data['categories']),
        'total_sales': len(data['sales']),
        'today_sales': len(today_sales),
        'month_sales': len(this_month),
        'total_revenue': sum(s['total'] for s in data['sales'] if s['status'] == 'completed'),
        'today_revenue': sum(s['total'] for s in today_sales if s['status'] == 'completed'),
        'month_revenue': sum(s['total'] for s in this_month if s['status'] == 'completed'),
        'low_stock_products': len([p for p in data['products'] if p['stock'] < p['min_stock'] and p['active']]),
        'total_customers': len(data['customers']),
        'active_users': len([u for u in data['users'] if u['active']]),
        'pending_sales': len([s for s in data['sales'] if s['status'] == 'pending']),
        'cancelled_sales': len([s for s in data['sales'] if s['status'] == 'cancelled'])
    }

@app.route('/api/products')
@login_required
def get_products():
    data = db.load_data()
    return jsonify([p for p in data['products'] if p['active']])

@app.route('/api/products/all')
@login_required
@role_required('admin')
def get_all_products():
    data = db.load_data()
    return jsonify(data['products'])

@app.route('/api/products/<int:product_id>')
@login_required
def get_product(product_id):
    data = db.load_data()
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    return jsonify(product) if product else jsonify({'error': 'Product not found'}), 404

@app.route('/api/products', methods=['POST'])
@login_required
@role_required('admin')
def create_product():
    data = db.load_data()
    product_data = request.json
    
    new_id = max([p['id'] for p in data['products']], default=0) + 1
    product = {
        'id': new_id,
        'name': product_data['name'],
        'sku': product_data['sku'],
        'barcode': product_data.get('barcode', ''),
        'price': float(product_data['price']),
        'cost': float(product_data.get('cost', 0)),
        'stock': int(product_data['stock']),
        'min_stock': int(product_data.get('min_stock', 5)),
        'category_id': int(product_data['category_id']),
        'supplier': product_data.get('supplier', ''),
        'description': product_data.get('description', ''),
        'weight': float(product_data.get('weight', 0)),
        'dimensions': product_data.get('dimensions', ''),
        'warranty': product_data.get('warranty', ''),
        'active': True,
        'created_at': datetime.now().isoformat()
    }
    
    data['products'].append(product)
    
    # Add inventory transaction
    data['inventory_transactions'].append({
        'id': len(data['inventory_transactions']) + 1,
        'product_id': new_id,
        'transaction_type': 'initial',
        'quantity': product['stock'],
        'reference': f'Product creation: {product["name"]}',
        'user_id': session['user_id'],
        'timestamp': datetime.now().isoformat(),
        'notes': f'New product added by {session["username"]}'
    })
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': session['user_id'],
        'action': 'create',
        'table': 'products',
        'record_id': new_id,
        'old_values': None,
        'new_values': product,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit real-time update
    socketio.emit('product_added', product)
    
    return jsonify(product)

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_product(product_id):
    data = db.load_data()
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    old_values = product.copy()
    update_data = request.json
    old_stock = product['stock']
    
    product.update({
        'name': update_data.get('name', product['name']),
        'sku': update_data.get('sku', product['sku']),
        'barcode': update_data.get('barcode', product['barcode']),
        'price': float(update_data.get('price', product['price'])),
        'cost': float(update_data.get('cost', product['cost'])),
        'stock': int(update_data.get('stock', product['stock'])),
        'min_stock': int(update_data.get('min_stock', product['min_stock'])),
        'category_id': int(update_data.get('category_id', product['category_id'])),
        'supplier': update_data.get('supplier', product['supplier']),
        'description': update_data.get('description', product['description']),
        'weight': float(update_data.get('weight', product['weight'])),
        'dimensions': update_data.get('dimensions', product['dimensions']),
        'warranty': update_data.get('warranty', product['warranty']),
        'active': update_data.get('active', product['active'])
    })
    
    # Add inventory transaction if stock changed
    if old_stock != product['stock']:
        data['inventory_transactions'].append({
            'id': len(data['inventory_transactions']) + 1,
            'product_id': product_id,
            'transaction_type': 'adjustment',
            'quantity': product['stock'] - old_stock,
            'reference': f'Stock adjustment: {product["name"]}',
            'user_id': session['user_id'],
            'timestamp': datetime.now().isoformat(),
            'notes': f'Stock updated by {session["username"]}'
        })
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': session['user_id'],
        'action': 'update',
        'table': 'products',
        'record_id': product_id,
        'old_values': old_values,
        'new_values': product,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit real-time update
    socketio.emit('product_updated', product)
    
    return jsonify(product)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_product(product_id):
    data = db.load_data()
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Soft delete - mark as inactive
    product['active'] = False
    
    # Add inventory transaction
    data['inventory_transactions'].append({
        'id': len(data['inventory_transactions']) + 1,
        'product_id': product_id,
        'transaction_type': 'deleted',
        'quantity': -product['stock'],
        'reference': f'Product deleted: {product["name"]}',
        'user_id': session['user_id'],
        'timestamp': datetime.now().isoformat(),
        'notes': f'Product deactivated by {session["username"]}'
    })
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': session['user_id'],
        'action': 'delete',
        'table': 'products',
        'record_id': product_id,
        'old_values': product,
        'new_values': {'active': False},
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit real-time update
    socketio.emit('product_deleted', {'id': product_id})
    
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/sales')
@login_required
def get_sales():
    data = db.load_data()
    return jsonify(data['sales'])

@app.route('/api/sales/recent')
@login_required
def get_recent_sales():
    data = db.load_data()
    recent_sales = sorted(data['sales'], key=lambda x: x['sale_date'], reverse=True)[:10]
    return jsonify(recent_sales)

@app.route('/api/customer/orders/pending')
@login_required
@role_required('admin', 'cashier')
def get_pending_customer_orders():
    data = db.load_data()
    pending_orders = [s for s in data['sales'] if s.get('status') == 'pending' and s.get('customer_id')]
    return jsonify(pending_orders)

@app.route('/api/customer/orders/process', methods=['POST'])
@login_required
@role_required('admin', 'cashier')
def process_customer_order():
    data = db.load_data()
    sale_id = request.json.get('sale_id')
    processed_by = session['user_id']
    
    # Find the sale
    sale = next((s for s in data['sales'] if s['id'] == sale_id), None)
    if not sale:
        return jsonify({'error': 'Order not found'}), 404
    
    # Update sale status
    sale['status'] = 'completed'
    sale['payment_status'] = 'paid'
    sale['processed_by'] = processed_by
    sale['processed_date'] = datetime.now().isoformat()
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': processed_by,
        'action': 'process_order',
        'table': 'sales',
        'record_id': sale_id,
        'old_values': {'status': 'pending'},
        'new_values': {'status': 'completed', 'processed_by': processed_by},
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit WebSocket event
    socketio.emit('order_processed', {
        'sale_id': sale_id,
        'sale_number': sale['sale_number'],
        'customer_id': sale['customer_id'],
        'status': 'completed'
    })
    
    return jsonify({'success': True, 'sale': sale})

@app.route('/api/sale', methods=['POST'])
@login_required
@role_required('admin', 'cashier')
def create_sale():
    data = db.load_data()
    sale_data = request.json
    
    # Generate new sale number
    sale_number = f'SALE-{str(len(data["sales"]) + 1).zfill(4)}'
    invoice_number = f'INV-{str(len(data["sales"]) + 1).zfill(4)}'
    new_id = len(data['sales']) + 1
    
    sale = {
        'id': new_id,
        'sale_number': sale_number,
        'invoice_number': invoice_number,
        'customer_id': sale_data.get('customer_id'),
        'user_id': session['user_id'],
        'items': sale_data['items'],
        'subtotal': float(sale_data['subtotal']),
        'tax': float(sale_data['tax']),
        'discount': float(sale_data.get('discount', 0)),
        'total': float(sale_data['total']),
        'payment_method': sale_data['payment_method'],
        'status': 'completed',
        'sale_date': datetime.now().isoformat(),
        'notes': sale_data.get('notes', ''),
        'shipping_address': sale_data.get('shipping_address'),
        'billing_address': sale_data.get('billing_address')
    }
    
    # Update product stock
    for item in sale['items']:
        product = next((p for p in data['products'] if p['id'] == item['product_id']), None)
        if product:
            product['stock'] -= item['quantity']
            
            # Add inventory transaction
            data['inventory_transactions'].append({
                'id': len(data['inventory_transactions']) + 1,
                'product_id': item['product_id'],
                'transaction_type': 'sale',
                'quantity': -item['quantity'],
                'reference': f'Sale {sale_number}',
                'user_id': session['user_id'],
                'timestamp': datetime.now().isoformat(),
                'notes': f'Product sold: {product["name"]}'
            })
    
    data['sales'].append(sale)
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': session['user_id'],
        'action': 'create',
        'table': 'sales',
        'record_id': new_id,
        'old_values': None,
        'new_values': {'sale_number': sale_number, 'total': sale['total']},
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit real-time updates
    socketio.emit('sale_completed', sale)
    
    # Check for low stock alerts
    low_stock_products = [p for p in data['products'] if p['stock'] < p['min_stock'] and p['active']]
    if low_stock_products:
        socketio.emit('inventory_alert', low_stock_products)
    
    return jsonify(sale)

@app.route('/api/customers')
@login_required
def get_customers():
    data = db.load_data()
    return jsonify(data['customers'])

@app.route('/api/customers', methods=['POST'])
@login_required
@role_required('admin', 'cashier')
def create_customer():
    data = db.load_data()
    customer_data = request.json
    
    new_id = max([c['id'] for c in data['customers']], default=0) + 1
    customer = {
        'id': new_id,
        'name': customer_data['name'],
        'email': customer_data['email'],
        'phone': customer_data.get('phone', ''),
        'address': customer_data.get('address', ''),
        'city': customer_data.get('city', ''),
        'state': customer_data.get('state', ''),
        'zip': customer_data.get('zip', ''),
        'country': customer_data.get('country', 'USA'),
        'company': customer_data.get('company', 'Individual'),
        'customer_type': customer_data.get('customer_type', 'individual'),
        'credit_limit': float(customer_data.get('credit_limit', 1000)),
        'created_at': datetime.now().isoformat()
    }
    
    data['customers'].append(customer)
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': session['user_id'],
        'action': 'create',
        'table': 'customers',
        'record_id': new_id,
        'old_values': None,
        'new_values': {'name': customer['name'], 'email': customer['email']},
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    db.save_data(data)
    
    # Emit real-time update
    socketio.emit('customer_added', customer)
    
    return jsonify(customer)

@app.route('/api/categories')
@login_required
def get_categories():
    data = db.load_data()
    return jsonify(data['categories'])

@app.route('/api/users')
@login_required
@role_required('admin')
def get_users():
    data = db.load_data()
    return jsonify(data['users'])

@app.route('/api/inventory/alerts')
@login_required
def get_inventory_alerts():
    data = db.load_data()
    low_stock = [p for p in data['products'] if p['stock'] < p['min_stock'] and p['active']]
    return jsonify(low_stock)

@app.route('/api/inventory/transactions')
@login_required
@role_required('admin')
def get_inventory_transactions():
    data = db.load_data()
    return jsonify(data['inventory_transactions'])

@app.route('/api/audit/logs')
@login_required
@role_required('admin')
def get_audit_logs():
    data = db.load_data()
    return jsonify(data['audit_logs'])

# Customer-specific API endpoints
@app.route('/api/customer/stats')
@login_required
@role_required('customer')
def get_customer_stats():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer profile
    customer_profile = next((cp for cp in data['customer_profiles'] if cp['user_id'] == user_id), None)
    
    # Get customer's orders
    customer_orders = [s for s in data['sales'] if s.get('customer_id') == user_id]
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    # Get customer's wishlist
    wishlist = next((w for w in data['wishlists'] if w['customer_id'] == user_id), None)
    
    # Calculate stats
    total_orders = len(customer_orders)
    total_spent = sum(s['total'] for s in customer_orders)
    total_items = sum(len(s['items']) for s in customer_orders)
    
    return jsonify({
        'total_orders': total_orders,
        'total_spent': total_spent,
        'total_items': total_items,
        'loyalty_points': customer_profile['loyalty_points'] if customer_profile else 0,
        'loyalty_tier': customer_profile['loyalty_tier'] if customer_profile else 'Bronze',
        'cart_items': len(shopping_cart['items']) if shopping_cart else 0,
        'wishlist_items': len(wishlist['items']) if wishlist else 0,
        'avg_order_value': total_spent / total_orders if total_orders > 0 else 0
    })

@app.route('/api/customer/orders')
@login_required
@role_required('customer')
def get_customer_orders():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer's orders
    customer_orders = [s for s in data['sales'] if s.get('customer_id') == user_id]
    
    # Sort by date (most recent first)
    customer_orders.sort(key=lambda x: x['sale_date'], reverse=True)
    
    return jsonify(customer_orders)

@app.route('/api/customer/cart')
@login_required
@role_required('customer')
def get_customer_cart():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart:
        return jsonify({'items': [], 'total': 0.0})
    
    return jsonify(shopping_cart)

@app.route('/api/customer/cart/add', methods=['POST'])
@login_required
@role_required('customer')
def add_to_cart():
    data = db.load_data()
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    # Get product
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product['stock'] < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart:
        # Create new shopping cart
        shopping_cart = {
            'id': len(data['shopping_carts']) + 1,
            'customer_id': user_id,
            'items': [],
            'total': 0.0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        data['shopping_carts'].append(shopping_cart)
    
    # Check if product already in cart
    existing_item = next((item for item in shopping_cart['items'] if item['product_id'] == product_id), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        shopping_cart['items'].append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'subtotal': product['price'] * quantity
        })
    
    # Recalculate total
    shopping_cart['total'] = sum(item['subtotal'] for item in shopping_cart['items'])
    shopping_cart['updated_at'] = datetime.now().isoformat()
    
    db.save_data(data)
    
    return jsonify({'success': True, 'cart': shopping_cart})

@app.route('/api/customer/cart/remove', methods=['POST'])
@login_required
@role_required('customer')
def remove_from_cart():
    data = db.load_data()
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # Remove item from cart
    shopping_cart['items'] = [item for item in shopping_cart['items'] if item['product_id'] != product_id]
    
    # Recalculate total
    shopping_cart['total'] = sum(item['price'] * item['quantity'] for item in shopping_cart['items'])
    shopping_cart['updated_at'] = datetime.now().isoformat()
    
    db.save_data(data)
    
    return jsonify({'success': True, 'cart': shopping_cart})

@app.route('/api/customer/cart/update', methods=['POST'])
@login_required
@role_required('customer')
def update_cart_quantity():
    data = db.load_data()
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    new_quantity = request.json.get('quantity')
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # Find and update item quantity
    cart_item = next((item for item in shopping_cart['items'] if item['product_id'] == product_id), None)
    
    if not cart_item:
        return jsonify({'error': 'Item not found in cart'}), 404
    
    # Check stock availability
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    if product and product.stock < new_quantity:
        return jsonify({'error': f'Only {product.stock} items available in stock'}), 400
    
    cart_item['quantity'] = new_quantity
    cart_item['subtotal'] = cart_item['price'] * new_quantity
    
    # Recalculate total
    shopping_cart['total'] = sum(item['price'] * item['quantity'] for item in shopping_cart['items'])
    shopping_cart['updated_at'] = datetime.now().isoformat()
    
    db.save_data(data)
    
    return jsonify({'success': True, 'cart': shopping_cart})

@app.route('/api/customer/cart/clear', methods=['POST'])
@login_required
@role_required('customer')
def clear_cart():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # Clear cart
    shopping_cart['items'] = []
    shopping_cart['total'] = 0.0
    shopping_cart['updated_at'] = datetime.now().isoformat()
    
    db.save_data(data)
    
    return jsonify({'success': True, 'cart': shopping_cart})

@app.route('/api/customer/wishlist')
@login_required
@role_required('customer')
def get_customer_wishlist():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer's wishlist
    wishlist = next((w for w in data['wishlists'] if w['customer_id'] == user_id), None)
    
    if not wishlist:
        return jsonify({'items': []})
    
    return jsonify(wishlist)

@app.route('/api/customer/wishlist/add', methods=['POST'])
@login_required
@role_required('customer')
def add_to_wishlist():
    data = db.load_data()
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    
    # Get product
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get customer's wishlist
    wishlist = next((w for w in data['wishlists'] if w['customer_id'] == user_id), None)
    
    if not wishlist:
        # Create new wishlist
        wishlist = {
            'id': len(data['wishlists']) + 1,
            'customer_id': user_id,
            'items': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        data['wishlists'].append(wishlist)
    
    # Check if product already in wishlist
    if not any(item['product_id'] == product_id for item in wishlist['items']):
        wishlist['items'].append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'added_at': datetime.now().isoformat()
        })
        wishlist['updated_at'] = datetime.now().isoformat()
        db.save_data(data)
    
    return jsonify({'success': True, 'wishlist': wishlist})

@app.route('/api/customer/wishlist/remove', methods=['POST'])
@login_required
@role_required('customer')
def remove_from_wishlist():
    data = db.load_data()
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    
    # Get customer's wishlist
    wishlist = next((w for w in data['wishlists'] if w['customer_id'] == user_id), None)
    
    if not wishlist:
        return jsonify({'error': 'Wishlist not found'}), 404
    
    # Remove item from wishlist
    wishlist['items'] = [item for item in wishlist['items'] if item['product_id'] != product_id]
    wishlist['updated_at'] = datetime.now().isoformat()
    
    db.save_data(data)
    
    return jsonify({'success': True, 'wishlist': wishlist})

@app.route('/api/customer/profiles')
@login_required
@role_required('admin', 'cashier')
def get_customer_profiles():
    data = db.load_data()
    return jsonify(data['customer_profiles'])

@app.route('/api/customer/<int:customer_id>/orders')
@login_required
@role_required('admin', 'cashier')
def get_customer_orders_by_id(customer_id):
    data = db.load_data()
    
    # Get customer's orders
    customer_orders = [s for s in data['sales'] if s.get('customer_id') == customer_id]
    
    # Sort by date (most recent first)
    customer_orders.sort(key=lambda x: x['sale_date'], reverse=True)
    
    return jsonify(customer_orders)

@app.route('/api/customer/profile', methods=['GET', 'PUT'])
@login_required
@role_required('customer')
def customer_profile():
    data = db.load_data()
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Get customer profile
        customer_profile = next((cp for cp in data['customer_profiles'] if cp['user_id'] == user_id), None)
        
        if not customer_profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(customer_profile)
    
    elif request.method == 'PUT':
        # Update customer profile
        customer_profile = next((cp for cp in data['customer_profiles'] if cp['user_id'] == user_id), None)
        
        if not customer_profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile_data = request.json
        
        # Update profile fields
        customer_profile.update({
            'phone': profile_data.get('phone', customer_profile['phone']),
            'address': profile_data.get('address', customer_profile['address']),
            'city': profile_data.get('city', customer_profile['city']),
            'state': profile_data.get('state', customer_profile['state']),
            'zip_code': profile_data.get('zip_code', customer_profile['zip_code']),
            'country': profile_data.get('country', customer_profile['country']),
            'email_notifications': profile_data.get('email_notifications', customer_profile['email_notifications']),
            'sms_notifications': profile_data.get('sms_notifications', customer_profile['sms_notifications']),
            'updated_at': datetime.now().isoformat()
        })
        
        db.save_data(data)
        
        return jsonify({'success': True, 'profile': customer_profile})

@app.route('/api/customer/reviews', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def customer_reviews():
    data = db.load_data()
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Get customer's reviews
        customer_reviews = [r for r in data['customer_reviews'] if r['customer_id'] == user_id]
        return jsonify(customer_reviews)
    
    elif request.method == 'POST':
        # Add new review
        review_data = request.json
        
        # Check if customer already reviewed this product
        existing_review = next((r for r in data['customer_reviews'] 
                               if r['customer_id'] == user_id and r['product_id'] == review_data['product_id']), None)
        
        if existing_review:
            return jsonify({'error': 'You have already reviewed this product'}), 400
        
        new_review = {
            'id': len(data['customer_reviews']) + 1,
            'customer_id': user_id,
            'product_id': review_data['product_id'],
            'rating': review_data['rating'],
            'review': review_data['review'],
            'created_at': datetime.now().isoformat()
        }
        
        data['customer_reviews'].append(new_review)
        db.save_data(data)
        
        return jsonify({'success': True, 'review': new_review})

@app.route('/api/customer/checkout', methods=['POST'])
@login_required
@role_required('customer')
def customer_checkout():
    data = db.load_data()
    user_id = session['user_id']
    
    # Get customer profile
    customer_profile = next((cp for cp in data['customer_profiles'] if cp['user_id'] == user_id), None)
    
    if not customer_profile:
        return jsonify({'error': 'Customer profile not found'}), 404
    
    # Get customer's shopping cart
    shopping_cart = next((sc for sc in data['shopping_carts'] if sc['customer_id'] == user_id), None)
    
    if not shopping_cart or not shopping_cart['items']:
        return jsonify({'error': 'Cart is empty'}), 400
    
    checkout_data = request.json
    payment_method = checkout_data.get('payment_method', 'cash')
    delivery_address = checkout_data.get('delivery_address', customer_profile.get('address', ''))
    
    # Generate new sale number and invoice
    sale_number = f'SALE-{str(len(data["sales"]) + 1).zfill(4)}'
    invoice_number = f'INV-{str(len(data["sales"]) + 1).zfill(4)}'
    new_id = len(data['sales']) + 1
    
    # Create sale record with customer details
    sale = {
        'id': new_id,
        'sale_number': sale_number,
        'invoice_number': invoice_number,
        'customer_id': user_id,
        'customer_name': customer_profile.get('full_name', 'Unknown'),
        'customer_email': customer_profile.get('email', ''),
        'customer_phone': customer_profile.get('phone', ''),
        'customer_address': delivery_address,
        'items': shopping_cart['items'].copy(),
        'subtotal': shopping_cart['total'],
        'tax': shopping_cart['total'] * data['settings'].get('tax_rate', 0.08),
        'total': shopping_cart['total'] * (1 + data['settings'].get('tax_rate', 0.08)),
        'payment_method': payment_method,
        'payment_status': 'pending',
        'status': 'pending',
        'sale_date': datetime.now().isoformat(),
        'processed_by': None,  # Will be set when admin processes
        'processed_date': None,
        'notes': checkout_data.get('notes', '')
    }
    
    # Add sale to database
    data['sales'].append(sale)
    
    # Update product stock
    for item in shopping_cart['items']:
        product = next((p for p in data['products'] if p['id'] == item['product_id']), None)
        if product:
            product['stock'] -= item['quantity']
            
            # Add inventory transaction
            inventory_transaction = {
                'id': len(data['inventory_transactions']) + 1,
                'product_id': item['product_id'],
                'transaction_type': 'sale',
                'quantity': -item['quantity'],
                'reference': sale_number,
                'notes': f'Sale to {customer_profile.get("full_name", "Unknown")}',
                'timestamp': datetime.now().isoformat()
            }
            data['inventory_transactions'].append(inventory_transaction)
    
    # Update customer profile
    customer_profile['total_orders'] += 1
    customer_profile['total_spent'] += sale['total']
    customer_profile['loyalty_points'] += int(sale['total'] * data['settings'].get('loyalty_points_per_dollar', 1))
    
    # Update loyalty tier based on points
    loyalty_programs = data.get('loyalty_programs', [])
    for program in sorted(loyalty_programs, key=lambda x: x['points_required'], reverse=True):
        if customer_profile['loyalty_points'] >= program['points_required']:
            customer_profile['loyalty_tier'] = program['name']
            break
    
    # Clear shopping cart
    shopping_cart['items'] = []
    shopping_cart['total'] = 0.0
    shopping_cart['updated_at'] = datetime.now().isoformat()
    
    # Add audit log
    data['audit_logs'].append({
        'id': len(data['audit_logs']) + 1,
        'user_id': user_id,
        'action': 'checkout',
        'table': 'sales',
        'record_id': new_id,
        'old_values': None,
        'new_values': {
            'sale_number': sale_number,
            'total': sale['total'],
            'customer_id': user_id
        },
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr
    })
    
    # Save data
    db.save_data(data)
    
    # Emit WebSocket event for admin notification
    socketio.emit('new_customer_order', {
        'sale_id': new_id,
        'sale_number': sale_number,
        'customer_name': customer_profile.get('full_name', 'Unknown'),
        'total': sale['total'],
        'status': 'pending'
    })
    
    return jsonify({
        'success': True,
        'sale': sale,
        'message': 'Order placed successfully! Your order is being processed.'
    })


@app.route('/api/analytics/sales-trend')
@login_required
def get_sales_trend():
    data = db.load_data()
    sales = data['sales']
    
    # Group sales by date
    sales_by_date = {}
    for sale in sales:
        if sale['status'] == 'completed':
            date = datetime.fromisoformat(sale['sale_date']).date().isoformat()
            if date not in sales_by_date:
                sales_by_date[date] = 0
            sales_by_date[date] += sale['total']
    
    # Sort by date
    sorted_dates = sorted(sales_by_date.keys())
    trend_data = {
        'dates': sorted_dates,
        'values': [sales_by_date[date] for date in sorted_dates]
    }
    
    return jsonify(trend_data)

@app.route('/api/analytics/category-performance')
@login_required
def get_category_performance():
    data = db.load_data()
    
    # Calculate sales by category
    category_sales = {}
    for sale in data['sales']:
        if sale['status'] == 'completed':
            for item in sale['items']:
                product = next((p for p in data['products'] if p['id'] == item['product_id']), None)
                if product:
                    category = next((c for c in data['categories'] if c['id'] == product['category_id']), None)
                    if category:
                        if category['name'] not in category_sales:
                            category_sales[category['name']] = 0
                        category_sales[category['name']] += item['total_price']
    
    return jsonify(category_sales)

@app.route('/api/analytics/top-products')
@login_required
def get_top_products():
    data = db.load_data()
    
    # Calculate product sales
    product_sales = {}
    for sale in data['sales']:
        if sale['status'] == 'completed':
            for item in sale['items']:
                if item['product_id'] not in product_sales:
                    product_sales[item['product_id']] = {
                        'name': item['product_name'],
                        'quantity': 0,
                        'revenue': 0
                    }
                product_sales[item['product_id']]['quantity'] += item['quantity']
                product_sales[item['product_id']]['revenue'] += item['total_price']
    
    # Sort by revenue
    top_products = sorted(product_sales.values(), key=lambda x: x['revenue'], reverse=True)[:10]
    
    return jsonify(top_products)

@app.route('/api/analytics/customer-analysis')
@login_required
def get_customer_analysis():
    data = db.load_data()
    
    # Calculate customer metrics
    customer_metrics = []
    for customer in data['customers']:
        customer_sales = [s for s in data['sales'] if s['customer_id'] == customer['id'] and s['status'] == 'completed']
        total_spent = sum(s['total'] for s in customer_sales)
        avg_order = total_spent / len(customer_sales) if customer_sales else 0
        
        customer_metrics.append({
            'name': customer['name'],
            'total_orders': len(customer_sales),
            'total_spent': total_spent,
            'avg_order_value': avg_order
        })
    
    # Sort by total spent
    customer_metrics.sort(key=lambda x: x['total_spent'], reverse=True)
    
    return jsonify(customer_metrics[:10])

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'Connected to E-Commerce Monitoring System', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        # Handle room joining for real-time updates
        print(f'Client joined room: {room}')

if __name__ == '__main__':
    print("=" * 60)
    print("E-COMMERCE MONITORING SYSTEM - COMPLETE VERSION")
    print("=" * 60)
    print("Starting application...")
    print("Access URL: http://localhost:5000")
    print("Default Login Credentials:")
    print("  Admin: admin / admin123")
    print("  Cashier: cashier / cashier123")
    print("Customer Registration: http://localhost:5000/register")
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
