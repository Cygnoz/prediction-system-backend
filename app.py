from flask import Flask, jsonify, request
from pymongo import MongoClient
from urllib.parse import quote_plus
import logging
import bcrypt

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# MongoDB credentials
username = "nexdeveloper1"
password = "nexdeveloper1"  # Replace with your actual password 

# URL-encode username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# MongoDB connection string
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

# Attempt to connect to MongoDB
try:
    client = MongoClient(mongodb_uri)
    db = client.get_database("Prediction")
    real_data_collection = db.get_collection("real_data")
    users_collection = db.get_collection("users")  # Add users collection

    logging.info("MongoDB connected successfully")

except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")

# Example route to fetch data from MongoDB
@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        data = list(real_data_collection.find({}, {'_id': 0}))  # Fetch all data, excluding _id
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        return jsonify({"error": str(e)}), 400

# Example route to insert data into MongoDB
@app.route('/api/add_data', methods=['POST'])
def add_data():
    try:
        new_data = request.json  # Get JSON data from the request
        real_data_collection.insert_one(new_data)  # Insert data into MongoDB
        return jsonify({"message": "Data added successfully"}), 201
    except Exception as e:
        logging.error(f"Error inserting data into MongoDB: {e}")
        return jsonify({"error": str(e)}), 400

# Hash password function
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Check password function
def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Route for user registration
@app.route('/api/register', methods=['POST'])
def register():
    try:
        # Get JSON data from request
        user_data = request.json
        username = user_data.get('username')
        password = user_data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Check if user already exists
        if users_collection.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400

        # Hash the password
        hashed_password = hash_password(password)

        # Store user data in MongoDB
        users_collection.insert_one({
            "username": username,
            "password": hashed_password.decode('utf-8')  # Store as string
        })

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        logging.error(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500


# Route for user login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        # Get JSON data from request
        credentials = request.json
        username = credentials.get('username')
        password = credentials.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Find the user with the provided username
        user = users_collection.find_one({"username": username})

        if user and check_password(user['password'].encode('utf-8'), password):
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
