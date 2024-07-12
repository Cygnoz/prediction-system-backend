import pymongo
from urllib.parse import quote_plus

# Define the credentials
username = "nexdeveloper1"
password = "nexdeveloper1"

# Encode the username and password for the URI
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Construct the MongoDB URI
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = pymongo.MongoClient(mongodb_uri)

# Access the database
mydb = client['Prediction']

# Define the new schema for the 'users' collection
schema = {
    "bsonType": "object",
    "required": ["username", "password"],
    "properties": {
        "username": {
            "bsonType": "string",
            "description": "must be a string and is required"
        },
        "password": {
            "bsonType": "string",
            "description": "must be a string and is required"
        }
    }
}

# Drop the collection if it already exists
mydb.drop_collection('users')

# Create the collection with schema validation
mydb.create_collection(
    'users',
    validator={
        "$jsonSchema": schema
    }
)

print("Collection created with schema validation.")
