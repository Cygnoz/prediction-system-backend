from flask import Flask, jsonify, request
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

# Original credentials
username = "nexdeveloper1"
password = "Nexdev@683562"

# URL-encoded credentials
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# MongoDB connection string with encoded credentials
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client.get_database("your_database_name")  # Replace with your database name
collection = db.get_collection("your_collection_name")  # Replace with your collection name

@app.route('/')
def home():
    return "Welcome to the Flask MongoDB server!"

@app.route('/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {"_id": 0}))  # Fetch all data from the collection
    return jsonify(data)

@app.route('/data', methods=['POST'])
def add_data():
    data = request.json
    collection.insert_one(data)
    return jsonify({"message": "Data added successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
