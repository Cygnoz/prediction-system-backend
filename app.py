from flask import Flask
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
    return "<h1>MongoDB connected Successfull</h1>"


if __name__ == '__main__':
    app.run(debug=True)
