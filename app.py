<<<<<<< HEAD


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for your app

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "this-is-a-secret-key"  # Change this later

# --- Extensions ---
db = SQLAlchemy(app)
jwt = JWTManager(app)


# --- Database Model ---
class User(db.Model):
    """Represents a user in the database."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks a password against the stored hash."""
        return check_password_hash(self.password_hash, password)


@app.route('/register', methods=['POST'])
def register():
    """Registers a new user, checking for duplicates first."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({"message": "Username, password, and email are required"}), 400

    # --- ADDED: Check for existing username or email ---
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 409  # 409 is the "Conflict" status code

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email address already registered"}), 409
    # --- END of added check ---

    new_user = User(
        username=data['username'],
        email=data['email'],
        address=data.get('address', '')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Logs in a user and returns a JWT."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password required"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid username or password"}), 401


@app.route('/users', methods=['GET'])
def get_users():
    """Returns a list of all registered users (for testing)."""
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'address': user.address
        }
        user_list.append(user_data)
    return jsonify(user_list), 200


# --- CLI Command ---
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")
=======

>>>>>>> 8fcb8e3b4ad4918473389cb5224a847c2abdfbe0
