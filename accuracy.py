# import requests
# import datetime

# BaseURL = "https://prediction.aisana.net:5000"

# def get_predictions(date):
#     url = f"{BaseURL}/api/get_predict?date={date}&n_predictions=10"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         return {
#             'morning': data.get('Morning_Predictions', []),
#             'afternoon': data.get('Afternoon_Predictions', []),
#             'evening': data.get('Evening_Predictions', [])
#         }
#     else:
#         return {}

# def fetch_data_from_api():
#     url = f"{BaseURL}/api/get_data"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return []

# def get_latest_actual_draw():
#     data = fetch_data_from_api()
    
#     # Check if data is a list of entries
#     if not isinstance(data, list):
#         raise ValueError("Expected the response to be a list.")
    
#     # Check for empty data
#     if not data:
#         raise ValueError("No draws found in the data.")
    
#     # Extract the latest entry
#     latest_entry = data[-1]  # Assuming the latest entry is the last one
    
#     # Extract draws from the latest entry
#     draws = latest_entry.get('draws', [])
    
#     if not draws:
#         raise ValueError("No draws available in the latest entry.")
    
#     # Get the most recent draw from the draws list
#     latest_draw = draws[-1]
    
#     return {
#         'morning': latest_draw.get('morning'),
#         'afternoon': latest_draw.get('afternoon'),
#         'evening': latest_draw.get('evening')
#     }

# def calculate_accuracy(predictions, actual):
#     def calculate_category_accuracy(preds, actuals):
#         if not preds or actuals is None:
#             return 0
#         # Count how many times the actual value appears in predictions
#         correct_predictions = preds.count(actuals)
#         return correct_predictions / len(preds) * 100 if preds else 0
    
#     accuracy = {
#         'morning': calculate_category_accuracy(predictions.get('morning', []), actual.get('morning')),
#         'afternoon': calculate_category_accuracy(predictions.get('afternoon', []), actual.get('afternoon')),
#         'evening': calculate_category_accuracy(predictions.get('evening', []), actual.get('evening')),
#     }
    
#     # Calculate overall accuracy as the average of category accuracies
#     overall_accuracy = sum(accuracy.values()) / len(accuracy) if accuracy else 0
#     return overall_accuracy

# def get_overall_accuracy():
#     today = datetime.date.today()
#     today_str = today.strftime("%y-%m-%d")
    
#     predictions_response = get_predictions(today_str)
#     morning_predictions = predictions_response.get('morning', [])
#     afternoon_predictions = predictions_response.get('afternoon', [])
#     evening_predictions = predictions_response.get('evening', [])
    
#     combined_predictions = morning_predictions + afternoon_predictions + evening_predictions
    
#     actual_response = get_latest_actual_draw()
    
#     actual_draws = {
#         'morning': actual_response.get('morning'),
#         'afternoon': actual_response.get('afternoon'),
#         'evening': actual_response.get('evening')
#     }
    
#     if not any(actual_draws.values()):  # Check if all values are empty
#         raise ValueError("Actual draws are incomplete.")
    
#     overall_accuracy = calculate_accuracy(predictions_response, actual_draws)
#     overall_accuracy = round(overall_accuracy, 1)
    
#     return {"overall_accuracy": overall_accuracy}

# if __name__ == "__main__":
#     try:
#         overall_accuracy = get_overall_accuracy()
#         print(f"Overall accuracy result: {overall_accuracy}")
#     except Exception as e:
#         print(f"An error occurred while calculating overall accuracy: {e}")

from datetime import datetime
import statistics
from pymongo import MongoClient
from urllib.parse import quote_plus
import pprint

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
db = client.get_database("Prediction")
real_data_collection = db["AllPredictions"]
predicted_data_collection = db["Predicted_data"]

def calculate_accuracy(real_value, predicted_values):
    errors = [abs(real_value - pred) for pred in predicted_values]
    mean_error = statistics.mean(errors)
    accuracy = max(0, 1 - (mean_error / real_value)) * 100
    return accuracy

def get_most_recent_data(collection):
    return collection.find_one(sort=[("_id", -1)])

def get_overall_accuracy():
    real_data = get_most_recent_data(real_data_collection)
    predicted_data = get_most_recent_data(predicted_data_collection)

    if not real_data or not predicted_data:
        print("No data available in one or both collections.")
        return

    print("Real data structure:")
    pprint.pprint(real_data)
    print("\nPredicted data structure:")
    pprint.pprint(predicted_data)

    real_date = real_data['draws'][0]['date']
    predicted_date = predicted_data['date']

    print(f"\nReal data date: {real_date}")
    print(f"Predicted data date: {predicted_date}")

    time_periods = ["morning", "afternoon", "evening"]
    results = {}

    try:
        for period in time_periods:
            real_value = real_data['draws'][0][period.lower()]
            predicted_values = predicted_data['value'][f'{period.capitalize()}_Predictions']
            
            accuracy = calculate_accuracy(real_value, predicted_values)
            results[period] = accuracy

        # Print results
        print("\nPrediction Accuracy for Most Recent Date:")
        for period, accuracy in results.items():
            print(f"{period.capitalize()}: {accuracy:.2f}%")

        overall_accuracy = statistics.mean(results.values())
        print(f"\nOverall Accuracy: {overall_accuracy:.2f}%")
        return overall_accuracy
    except KeyError as e:
        print(f"Error: Could not find the key {e} in the data. Please check the field names.")

if __name__ == "__main__":
    try:
        overall_accuracy = get_overall_accuracy()
        print(f"Overall accuracy result: {overall_accuracy}")
    except Exception as e:
        print(f"An error occurred while calculating overall accuracy: {e}")


