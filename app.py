from flask import Flask, jsonify
from pymongo import MongoClient
from urllib.parse import quote_plus
import logging

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
    collection = db.get_collection("real_data")

    logging.info("MongoDB connected successfully")

except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")

# Example route to fetch data from MongoDB
@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        data = list(collection.find({}, {'_id': 0}))  # Fetch all data, excluding _id
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
