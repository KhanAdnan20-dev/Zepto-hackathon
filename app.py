from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
app = Flask(__name__)

app.config['sqlite://users.db'] = 'sqlite:///users.db' #path to database server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False# Disable track modifications to save resources
db=SQLALchemy(app)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)    

    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)




@app.route('/register', methods=['POST'])
def register():
    data=request.get_json()
    new_user=User(username=data['username'],password=data['password'],
                    email=data['email'],address=data['address'])
    db.session.add(new_user)
    db.session.commit() 
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
  user=user.query.filter_by(username=data['username']).first()
if user and check_password_hash(user.password_hash, data['password']):
   
    print("User is valid.") #u
else:
    
    print("Invalid credentials.")
   