# import requests
# import datetime

# BaseURL = "http://127.0.0.1:5000"

# def get_predictions(date):
#     url = f"{BaseURL}/api/get_predict?date={date}&n_predictions=10"
#     print(f"Requesting predictions from: {url}")
#     response = requests.get(url)
#     print(f"Response status code: {response.status_code}")
#     print(f"Raw response content: {response.text}")
#     if response.status_code == 200:
#         data = response.json()
#         print(f"Parsed JSON data: {data}")
#         return {
#             'morning': data.get('Morning_Predictions', []),
#             'afternoon': data.get('Afternoon_Predictions', []),
#             'evening': data.get('Evening_Predictions', [])
#         }
#     else:
#         print(f"Failed to get predictions: {response.text}")
#         return {}

# def fetch_data_from_api():
#     url = f"{BaseURL}/api/get_data"
#     print(f"Requesting actual draws from: {url}")
#     response = requests.get(url)
#     print(f"Response status code: {response.status_code}")
#     if response.status_code == 200:
#         print("Actual draws data received")
#         return response.json()
#     else:
#         print(f"Failed to get actual draws: {response.text}")
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
#     print(f"Today's date: {today_str}")
    
#     predictions_response = get_predictions(today_str)
#     morning_predictions = predictions_response.get('morning', [])
#     afternoon_predictions = predictions_response.get('afternoon', [])
#     evening_predictions = predictions_response.get('evening', [])
    
#     print(f"Morning predictions: {morning_predictions}")
#     print(f"Afternoon predictions: {afternoon_predictions}")
#     print(f"Evening predictions: {evening_predictions}")
    
#     combined_predictions = morning_predictions + afternoon_predictions + evening_predictions
#     print(f"Combined predictions: {combined_predictions}")
    
#     actual_response = get_latest_actual_draw()
#     print(f"Actual response: {actual_response}")
    
#     actual_draws = {
#         'morning': actual_response.get('morning'),
#         'afternoon': actual_response.get('afternoon'),
#         'evening': actual_response.get('evening')
#     }
    
#     print(f"Actual draws: {actual_draws}")
    
#     if not any(actual_draws.values()):  # Check if all values are empty
#         raise ValueError("Actual draws are incomplete.")
    
#     overall_accuracy = calculate_accuracy(predictions_response, actual_draws)
#     overall_accuracy = round(overall_accuracy, 1)
    
#     print(f"Overall accuracy: {overall_accuracy}")
#     return {"overall_accuracy": overall_accuracy}

# if __name__ == "__main__":
#     overall_accuracy = get_overall_accuracy()
#     print(f"Overall accuracy result: {overall_accuracy}")




import requests
import datetime
import logging

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler("draw_prediction.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

BaseURL = "http://127.0.0.1:5000"

def get_predictions(date):
    url = f"{BaseURL}/api/get_predict?date={date}&n_predictions=10"
    logging.debug(f"Requesting predictions from: {url}")
    response = requests.get(url)
    logging.debug(f"Response status code: {response.status_code}")
    logging.debug(f"Raw response content: {response.text}")
    if response.status_code == 200:
        data = response.json()
        logging.debug(f"Parsed JSON data: {data}")
        return {
            'morning': data.get('Morning_Predictions', []),
            'afternoon': data.get('Afternoon_Predictions', []),
            'evening': data.get('Evening_Predictions', [])
        }
    else:
        logging.error(f"Failed to get predictions: {response.text}")
        return {}

def fetch_data_from_api():
    url = f"{BaseURL}/api/get_data"
    logging.debug(f"Requesting actual draws from: {url}")
    response = requests.get(url)
    logging.debug(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        logging.debug("Actual draws data received")
        return response.json()
    else:
        logging.error(f"Failed to get actual draws: {response.text}")
        return []

def get_latest_actual_draw():
    data = fetch_data_from_api()
    
    # Check if data is a list of entries
    if not isinstance(data, list):
        logging.error("Expected the response to be a list.")
        raise ValueError("Expected the response to be a list.")
    
    # Check for empty data
    if not data:
        logging.error("No draws found in the data.")
        raise ValueError("No draws found in the data.")
    
    # Extract the latest entry
    latest_entry = data[-1]  # Assuming the latest entry is the last one
    
    # Extract draws from the latest entry
    draws = latest_entry.get('draws', [])
    
    if not draws:
        logging.error("No draws available in the latest entry.")
        raise ValueError("No draws available in the latest entry.")
    
    # Get the most recent draw from the draws list
    latest_draw = draws[-1]
    
    return {
        'morning': latest_draw.get('morning'),
        'afternoon': latest_draw.get('afternoon'),
        'evening': latest_draw.get('evening')
    }

def calculate_accuracy(predictions, actual):
    def calculate_category_accuracy(preds, actuals):
        if not preds or actuals is None:
            return 0
        # Count how many times the actual value appears in predictions
        correct_predictions = preds.count(actuals)
        return correct_predictions / len(preds) * 100 if preds else 0
    
    accuracy = {
        'morning': calculate_category_accuracy(predictions.get('morning', []), actual.get('morning')),
        'afternoon': calculate_category_accuracy(predictions.get('afternoon', []), actual.get('afternoon')),
        'evening': calculate_category_accuracy(predictions.get('evening', []), actual.get('evening')),
    }
    
    # Calculate overall accuracy as the average of category accuracies
    overall_accuracy = sum(accuracy.values()) / len(accuracy) if accuracy else 0
    return overall_accuracy

def get_overall_accuracy():
    today = datetime.date.today()
    today_str = today.strftime("%y-%m-%d")
    logging.debug(f"Today's date: {today_str}")
    
    predictions_response = get_predictions(today_str)
    morning_predictions = predictions_response.get('morning', [])
    afternoon_predictions = predictions_response.get('afternoon', [])
    evening_predictions = predictions_response.get('evening', [])
    
    logging.debug(f"Morning predictions: {morning_predictions}")
    logging.debug(f"Afternoon predictions: {afternoon_predictions}")
    logging.debug(f"Evening predictions: {evening_predictions}")
    
    combined_predictions = morning_predictions + afternoon_predictions + evening_predictions
    logging.debug(f"Combined predictions: {combined_predictions}")
    
    actual_response = get_latest_actual_draw()
    logging.debug(f"Actual response: {actual_response}")
    
    actual_draws = {
        'morning': actual_response.get('morning'),
        'afternoon': actual_response.get('afternoon'),
        'evening': actual_response.get('evening')
    }
    
    logging.debug(f"Actual draws: {actual_draws}")
    
    if not any(actual_draws.values()):  # Check if all values are empty
        logging.error("Actual draws are incomplete.")
        raise ValueError("Actual draws are incomplete.")
    
    overall_accuracy = calculate_accuracy(predictions_response, actual_draws)
    overall_accuracy = round(overall_accuracy, 1)
    
    logging.debug(f"Overall accuracy: {overall_accuracy}")
    return {"overall_accuracy": overall_accuracy}

if __name__ == "__main__":
    try:
        overall_accuracy = get_overall_accuracy()
        logging.info(f"Overall accuracy result: {overall_accuracy}")
    except Exception as e:
        logging.exception("An error occurred while calculating overall accuracy.")
