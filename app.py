import os
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-for-hackathon-phase-3'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'zepto.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Fix session issues
app.config['SESSION_COOKIE_SECURE'] = False    # Disable in development
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)  # Fix CORS issues

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Ensure this line exists
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', backref=db.backref('items', lazy=True, cascade="all, delete-orphan"))
    product = db.relationship('Product')

# --- API Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 409
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"Welcome, {data['username']}! Registration successful."}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        return jsonify({"message": f"Welcome back, {user.username}!", "username": user.username}), 200
    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/api/products', methods=['GET'])
def get_products():
    if 'user_id' not in session: 
        return jsonify({"message": "Please log in to see products."}), 401
    products = [{"id": p.id, "name": p.name, "price": p.price, "image_url": p.image_url} for p in Product.query.all()]
    return jsonify(products)

@app.route('/api/order', methods=['POST'])
def place_order():
    if 'user_id' not in session: 
        return jsonify({"message": "Please log in to place an order."}), 401
    
    cart_data = request.get_json()
    if not cart_data or len(cart_data) == 0: 
        return jsonify({"message": "Your cart is empty."}), 400
    
    try:
        new_order = Order(user_id=session['user_id'])
        db.session.add(new_order)
        db.session.flush()  # Get ID before commit
        
        for item in cart_data:
            # Validate product exists
            product = Product.query.get(item['id'])
            if not product:
                return jsonify({"message": f"Product {item['id']} not found"}), 404
                
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['id'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
            
        db.session.commit()
        return jsonify({
            "message": "Order placed successfully!",
            "order_id": new_order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error placing order: {str(e)}"}), 500

@app.route('/api/order/history', methods=['GET'])
def order_history():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_date.desc()).all()
    history = []
    for order in user_orders:
        # Calculate total
        total = sum(item.product.price * item.quantity for item in order.items)
        
        order_data = {
            "id": order.id,
            "date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{
                "id": item.product.id,
                "name": item.product.name, 
                "quantity": item.quantity, 
                "price": item.product.price
            } for item in order.items],
            "total": total
        }
        history.append(order_data)
    return jsonify(history)

@app.route('/api/order/<int:order_id>/status', methods=['GET'])
def order_status(order_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    order = Order.query.filter_by(id=order_id, user_id=session['user_id']).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    time_since_order = datetime.utcnow() - order.order_date
    status = "Order Confirmed"
    if time_since_order > timedelta(minutes=5):
        status = "Delivered"
    elif time_since_order > timedelta(minutes=3):
        status = "Out for Delivery"
    elif time_since_order > timedelta(minutes=1):
        status = "Packed"
    
    return jsonify({
        "order_id": order.id,
        "status": status,
        "timestamp": order.order_date.isoformat()
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)