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

# Define the new schema for the 'Predicted_data' collection
schema = {
    "bsonType": "object",
    "required": ["month", "year", "draws"],
    "properties": {
        "month": {
            "bsonType": "string",
            "description": "must be a string and is required"
        },
        "year": {
            "bsonType": "int",
            "description": "must be an integer and is required"
        },
        "draws": {
            "bsonType": "array",
            "description": "must be an array of draw documents and is required",
            "items": {
                "bsonType": "object",
                "required": ["date", "morning", "afternoon", "evening"],
                "properties": {
                    "date": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "morning": {
                        "bsonType": "double",
                        "description": "must be a double and is required"
                    },
                    "afternoon": {
                        "bsonType": "double",
                        "description": "must be a double and is required"
                    },
                    "evening": {
                        "bsonType": "double",
                        "description": "must be a double and is required"
                    }
                }
            }
        }
    }
}

# Drop the collection if it already exists
mydb.drop_collection('Predicted_data')

# Create the collection with schema validation
mydb.create_collection(
    'Predicted_data',
    validator={
        "$jsonSchema": schema
    }
)

print("Collection created with schema validation.")
