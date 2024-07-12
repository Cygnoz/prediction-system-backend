from flask import Flask, request, jsonify
from pymongo import MongoClient
from urllib.parse import quote_plus
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

app = Flask(__name__)

# MongoDB credentials
username = "nexdeveloper1"
password = "nexdeveloper1"  # Replace with your actual password

# URL-encode username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# MongoDB connection string
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(mongodb_uri)

# Get the database and collection
db = client.get_database("Prediction")
collection = db.get_collection("AllPredictions")

# Fetch data from the collection
predictions = collection.find()

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

@app.route('/predict', methods=['GET'])
def predict():
    date_str = request.args.get('date')
    n_predictions = int(request.args.get('n_predictions', 10))

    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        date_to_predict = pd.to_datetime(date_str)
        predictions = predict_winning_numbers(date_to_predict, n_predictions)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
