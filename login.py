from pymongo import MongoClient
from urllib.parse import quote_plus

# Database connection details
username = "nexdeveloper1"
password = "nexdeveloper1"  # Replace with your actual password 

# URL-encode username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# MongoDB connection string
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

def connect_to_db(uri):
    try:
        client = MongoClient(uri)
        db = client.get_database("Prediction")
        collection = db.get_collection("users")
        return collection
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None

def login(collection, input_username, input_password):
    try:
        # Find the user with the provided username
        user = collection.find_one({"username": input_username})
        
        if user:
            # Check if the provided password matches the stored password
            if user['password'] == input_password:
                return "Login successful"
            else:
                return "Incorrect password"
        else:
            return "Username not found"
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return "Login failed"

# Connect to the database
collection = connect_to_db(mongodb_uri)

if collection:
    # Example usage
    input_username = "test_user"  # Replace with the actual username
    input_password = "test_password"  # Replace with the actual password

    result = login(collection, input_username, input_password)
    print(result)
else:
    print("Failed to connect to the database.")
