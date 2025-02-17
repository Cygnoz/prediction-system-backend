from flask import Flask, jsonify, request
from pymongo import MongoClient
from urllib.parse import quote_plus
import logging
import bcrypt
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
from dateutil import parser
import accuracy
import threading
import time 
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

app = Flask(__name__)




CORS(app, resources={r"/*": {"origins": "https://prediction.aisana.net"}})

# CORS(app, resources={r"/*": {"origins":"*"}})



def set_x_frame_options(response):
    response.headers['X-Frame-Options'] = 'DENY'  # or 'SAMEORIGIN'
    return response

app.after_request(set_x_frame_options)

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
    real_data_collection = db.get_collection("AllPredictions")
    users_collection = db.get_collection("users")  # Add users collection
    predicted_data=db.get_collection("Predicted_data")
    draws_collection=db.get_collection("draws_collection")

    logging.info("MongoDB connected successfully")

except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Prediction System!"})

# Example route to fetch data from MongoDB
@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        print("get data request received")
        # # Fetch the latest 20 documents, excluding _id
        # data = list(real_data_collection.find({}, {'_id': 0}).sort([('timestamp', -1)]).limit(2))
        # Fetch all documents, excluding _id, and sort them in ascending order by timestamp
        data = list(real_data_collection.find({}, {'_id': 0}).sort([('timestamp', 1)]))
        print("get data request successful")
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        return jsonify({"error": str(e)}), 400
    
@app.route('/api/get_predict_data', methods=['GET'])
def get_predict_data():
    try:
        print("get predict data request received")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = datetime(2024, 7, 24)
        
        logging.info(f"Fetching data from {start_date} to {today}")
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": today
                    }
                }
            },
            {
                "$match": {
                    "$expr": {
                        "$not": {
                            "$or": [
                                {
                                    "$and": [
                                        {"$eq": [{"$dayOfMonth": "$date"}, 15]},
                                        {"$eq": [{"$month": "$date"}, 8]}
                                    ]
                                },
                                {
                                    "$and": [
                                        {"$eq": [{"$dayOfMonth": "$date"}, 2]},
                                        {"$eq": [{"$month": "$date"}, 10]}
                                    ]
                                },
                                {
                                    "$and": [
                                        {"$eq": [{"$dayOfMonth": "$date"}, 26]},
                                        {"$eq": [{"$month": "$date"}, 1]}
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$date",
                    "firstDocument": { "$first": "$$ROOT" }
                }
            },
            {
                "$replaceRoot": { "newRoot": "$firstDocument" }
            },
            {
                "$project": { "_id": 0 }
            },
            {
                "$sort": { "date": 1 }
            }
        ]
        
        logging.info(f"Aggregation pipeline: {pipeline}")
        
        unique_data = list(predicted_data.aggregate(pipeline))
        
        logging.info(f"Number of documents fetched: {len(unique_data)}")
        if unique_data:
            logging.info(f"First document: {unique_data[0]}")
            logging.info(f"Last document: {unique_data[-1]}")
        else:
            logging.warning("No documents fetched")
        
        total_count = predicted_data.count_documents({})
        # logging.info(f"Total documents in collection: {total_count}")
        print("get predict request succesfull")
        return jsonify(unique_data), 200
    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        return jsonify({"error": str(e)}), 400

#training sets
#
#
#
predictions = real_data_collection.find()

# Create an empty DataFrame
df = pd.DataFrame()

# Iterate over each month's data
for prediction in predictions:
    month = prediction['month']
    year = prediction['year']
    draws = prediction['draws']

    # Convert each day's draw to a DataFrame
    month_df = pd.DataFrame(draws)
    month_df['month'] = month
    month_df['year'] = year

    # Append to the main DataFrame
    df = pd.concat([df, month_df], ignore_index=True)

# Convert 'date' to datetime for better handling
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

# Handle missing values in 'afternoon' column
df['afternoon'] = pd.to_numeric(df['afternoon'], errors='coerce')
df.dropna(inplace=True)
df['afternoon'] = df['afternoon'].astype(float)

# Define features and targets
features = ['month', 'year']
X = pd.get_dummies(df[features])

# Target variables (last two digits of each draw time)
y_morning = df['morning'] % 100
y_afternoon = df['afternoon'] % 100
y_evening = df['evening'] % 100

# Train-test split for each target
X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(X, y_morning, test_size=0.2, random_state=42)
X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X, y_afternoon, test_size=0.2, random_state=42)
X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X, y_evening, test_size=0.2, random_state=42)

# Train the models
model_morning = RandomForestRegressor(n_estimators=100, random_state=42)
model_afternoon = RandomForestRegressor(n_estimators=100, random_state=42)
model_evening = RandomForestRegressor(n_estimators=100, random_state=42)

model_morning.fit(X_train_m, y_train_m)
model_afternoon.fit(X_train_a, y_train_a)
model_evening.fit(X_train_e, y_train_e)

# Save the models to disk
joblib.dump(model_morning, 'model_morning.pkl')
joblib.dump(model_afternoon, 'model_afternoon.pkl')
joblib.dump(model_evening, 'model_evening.pkl')

# Function to predict winning numbers
def predict_winning_numbers(date, n_predictions=10):
    # Prepare input features for prediction
    input_data = pd.DataFrame({
        'month': [date.strftime('%B')],
        'year': [date.year]
    })

    # Convert 'month' to categorical variable, consistent with training data
    input_data = pd.get_dummies(input_data, columns=['month'])

    # Get all the month columns used during training
    training_month_columns = X_train_m.columns[X_train_m.columns.str.startswith('month_')]

    # Ensure all one-hot encoded months from training are present in the prediction data
    for month in training_month_columns:
        if month not in input_data.columns:
            input_data[month] = 0

    # Reorder columns to match the order used during training
    input_data = input_data[X_train_m.columns]  # Use the column order from training data

    # Generate multiple predictions by fitting the model on different subsets of the training data
    morning_predictions = []
    afternoon_predictions = []
    evening_predictions = []

    for _ in range(n_predictions):
        # Shuffle and split the data
        X_train_m_shuffled, _, y_train_m_shuffled, _ = train_test_split(X_train_m, y_train_m, test_size=0.2, random_state=np.random.randint(10000))
        X_train_a_shuffled, _, y_train_a_shuffled, _ = train_test_split(X_train_a, y_train_a, test_size=0.2, random_state=np.random.randint(10000))
        X_train_e_shuffled, _, y_train_e_shuffled, _ = train_test_split(X_train_e, y_train_e, test_size=0.2, random_state=np.random.randint(10000))

        # Fit the models again
        model_morning.fit(X_train_m_shuffled, y_train_m_shuffled)
        model_afternoon.fit(X_train_a_shuffled, y_train_a_shuffled)
        model_evening.fit(X_train_e_shuffled, y_train_e_shuffled)

        # Predict winning numbers
        pred_morning = model_morning.predict(input_data)
        pred_afternoon = model_afternoon.predict(input_data)
        pred_evening = model_evening.predict(input_data)

        morning_predictions.append(np.round(pred_morning).astype(int).tolist()[0] % 100)
        afternoon_predictions.append(np.round(pred_afternoon).astype(int).tolist()[0] % 100)
        evening_predictions.append(np.round(pred_evening).astype(int).tolist()[0] % 100)

    # Return the top 10 predictions for each draw time
    return {
        'Morning_Predictions': morning_predictions,
        'Afternoon_Predictions': afternoon_predictions,
        'Evening_Predictions': evening_predictions
    }

cached_predictions = {}
cache_lock = threading.Lock()

def get_cache_key(date):
    return date.strftime("%Y-%m-%d")

@app.route('/api/get_predict', methods=['GET'])
def get_predict():
    date_str = request.args.get('date')
    n_predictions = int(request.args.get('n_predictions', 10))

    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        date_to_predict = pd.to_datetime(date_str)
        return generate_prediction(date_to_predict, n_predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_prediction(date_to_predict, n_predictions):
    cache_key = get_cache_key(date_to_predict)
    
    with cache_lock:
        if cache_key in cached_predictions:
            return jsonify(cached_predictions[cache_key])
        
        try:
            # If not in cache, generate new predictions
            predictions = predict_winning_numbers(date_to_predict, n_predictions)
            
            # Ensure date_to_predict is in a format that MongoDB can handle
            if isinstance(date_to_predict, pd.Timestamp):
                date_to_predict = date_to_predict.to_pydatetime()
            
            # Insert the new predictions into the database
            predicted_data.insert_one({"date": date_to_predict, "value": predictions})

            # Cache the new predictions
            cached_predictions[cache_key] = predictions
        except Exception as e:
            logging.error(f"Error generating or inserting predictions: {e}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify(predictions)

def automated_daily_prediction():
    today = datetime.now().date()
    # tomorrow = today + timedelta(days=1)
    
    app.logger.info(f"Generating prediction for {today}")
    
    with app.app_context():
        generate_prediction(today, 10)  # Assuming 10 predictions by default
    
    app.logger.info(f"Daily prediction for {today} completed")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=automated_daily_prediction,
    trigger=CronTrigger(hour=0, minute=5),  # Run at 00:05 every day
    id='daily_prediction_job',
    name='Generate daily prediction',
    replace_existing=True)

# Start the scheduler
scheduler.start()



# Initialize cache and lock
cached_predictions = {}
cache_lock = threading.Lock()

def clear_outdated_cache():
    global cached_predictions
    with cache_lock:
        current_date = datetime.now().date()
        cached_predictions = {
            k: v for k, v in cached_predictions.items()
            if pd.to_datetime(k).date() >= current_date
        }
    print(f"Cache cleared. Retained predictions from {current_date} onwards")

def clear_cache_at_midnight():
    while True:
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_midnight = (midnight - now).total_seconds()
        
        time.sleep(time_to_midnight)
        clear_outdated_cache()
        time.sleep(1)  # Wait 1 second before calculating next midnight

# Start the cache clearing thread only once when the app starts
threading.Thread(target=clear_cache_at_midnight, daemon=True).start()
#
#
#
#


# Example route to insert data into MongoDB
@app.route('/api/add_data', methods=['POST'])
def add_data():
    try:
        new_data = request.json  # Get JSON data from the request
 
        # Validate that all required fields are present
        required_fields = ['year', 'month', 'draws']
        for field in required_fields:
            if field not in new_data:
                return jsonify({"error": f"'{field}' is required"}), 400
 
        # Additional validation can be added here if needed
 
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
        print("login request received")
        credentials = request.json
        username = credentials.get('username')
        password = credentials.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Find the user with the provided username
        user = users_collection.find_one({"username": username})

        if user and check_password(user['password'].encode('utf-8'), password):
            print("login request succesful")
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/get_accuracy', methods=['GET'])
def get_accuracy():
    try:
        data = accuracy.get_overall_accuracy()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

