from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)  # Allow all origins

# Swagger configuration
swagger = Swagger(app)

# In-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Create tables within app context
with app.app_context():
    db.create_all()

# Redirect root "/" to Swagger UI
@app.route("/", methods=["GET"])
def home():
    return redirect("/apidocs/")

# CREATE User
@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - User
    parameters:
      - name: name
        in: formData
        type: string
        required: true
      - name: surname
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: User registered successfully
      400:
        description: Error registering user
    """
    data = request.form
    user = User(
        name=data.get("name"),
        surname=data.get("surname"),
        email=data.get("email"),
        password=data.get("password")
    )
    db.session.add(user)
    try:
        db.session.commit()
        return {"message": "User registered successfully"}
    except:
        db.session.rollback()
        return {"message": "Error registering user"}, 400

# READ all users
@app.route("/users", methods=["GET"])
def get_users():
    """
    Get all users
    ---
    tags:
      - User
    responses:
      200:
        description: List of users
    """
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "surname": u.surname,
        "email": u.email
    } for u in users])

# READ single user
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get a single user by ID
    ---
    tags:
      - User
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User found
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if user:
        return {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email
        }
    else:
        return {"message": "User not found"}, 404

# UPDATE user
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update a user by ID
    ---
    tags:
      - User
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: name
        in: formData
        type: string
      - name: surname
        in: formData
        type: string
      - name: email
        in: formData
        type: string
      - name: password
        in: formData
        type: string
    responses:
      200:
        description: User updated successfully
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    data = request.form
    user.name = data.get("name", user.name)
    user.surname = data.get("surname", user.surname)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)

    try:
        db.session.commit()
        return {"message": "User updated successfully"}
    except:
        db.session.rollback()
        return {"message": "Error updating user"}, 400

# DELETE user
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user by ID
    ---
    tags:
      - User
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Fly.io sets PORT
    app.run(host="0.0.0.0", port=port, debug=True)
