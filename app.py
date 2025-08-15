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

# -------------------------
# Models
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Create tables
with app.app_context():
    db.create_all()

# -------------------------
# Root redirect to Swagger
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return redirect("/apidocs/")

# -------------------------
# Documents endpoint (mock)
# -------------------------
@app.route("/documents", methods=["GET"])
def get_documents():
    """
    Get documents
    ---
    tags:
      - Documents
    responses:
      200:
        description: List of documents
    """
    docs = [
        {"id": "doc1", "title": "Document 1", "description": "Sample document 1"},
        {"id": "doc2", "title": "Document 2", "description": "Sample document 2"},
        {"id": "doc3", "title": "Document 3", "description": "Sample document 3"},
    ]
    return jsonify(docs)

# -------------------------
# Register
# -------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return {"success": False, "message": "No input data provided"}, 400

    if User.query.filter_by(email=data.get("email")).first():
        return {"success": False, "message": "Email already exists"}, 400

    user = User(
        name=data.get("name"),
        surname=data.get("surname"),
        email=data.get("email"),
        password=data.get("password")
    )
    db.session.add(user)
    try:
        db.session.commit()
        return {"success": True, "user": {"id": user.id, "name": user.name, "surname": user.surname, "email": user.email}}
    except:
        db.session.rollback()
        return {"success": False, "message": "Error registering user"}, 400

# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return {"success": False, "message": "No input data provided"}, 400

    user = User.query.filter_by(email=data.get("email"), password=data.get("password")).first()
    if user:
        return {"success": True, "user": {"id": user.id, "name": user.name, "surname": user.surname, "email": user.email}}
    return {"success": False, "message": "Invalid credentials"}, 401

# -------------------------
# Users CRUD (optional)
# -------------------------
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "surname": u.surname, "email": u.email} for u in users])

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return {"id": user.id, "name": user.name, "surname": user.surname, "email": user.email}
    return {"message": "User not found"}, 404

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    data = request.get_json()
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

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}

# -------------------------
# Run Flask
# -------------------------
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
