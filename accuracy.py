
import random

# Generate array of numbers from 10 to 99
numbers_array = [str(i).zfill(2) for i in range(16, 100)]
print(numbers_array)

# Choose a random number from the array
random_number = random.choice(numbers_array)
print(f"Random number: {random_number}")




# # 
# # 
# # 
# # 
# from pymongo import MongoClient
# from urllib.parse import quote_plus

# username = "nexdeveloper1"
# password = "nexdeveloper1"

# encoded_password = quote_plus(password)
# encoded_username = quote_plus(username)

# # MongoDB connection string
# mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

# def get_data_from_mongo():
#     # Set up MongoDB connection
#     client = MongoClient(mongodb_uri)
#     db = client['Prediction']  # Correct database name
    
#     # Fetch predicted values
#     predicted_collection = db['Predicted_data']  # Correct predicted collection name
#     predicted_docs = predicted_collection.find({})
#     predicted = [doc['value'] for doc in predicted_docs]  # Update the field name if needed

#     # Fetch actual values
#     actual_collection = db['AllPredictions']  # Correct actual collection name
#     actual_docs = actual_collection.find({})
#     actual = [doc['draws'] for doc in actual_docs]  # Update the field name if needed

#     return predicted, actual

# # Fetch data from MongoDB
# predicted, actual = get_data_from_mongo()

# # Ensure predicted and actual values have data
# if not predicted or not actual:
#     raise ValueError("Predicted and/or actual values are empty. Please check the database collections.")

# # Assuming actual has morning, afternoon, and evening values
# # an
# def calculate_accuracy(predicted, actual):
#     """
#     Calculate the accuracy of predictions against the actual values.

#     :param predicted: List of predicted numbers.
#     :param actual: List of actual numbers.
#     :return: Accuracy as a percentage.
#     """
#     if len(predicted) != len(actual):
#         raise ValueError("Length of predicted and actual lists must be the same.")
    
#     correct_predictions = 0
    
#     for pred, act in zip(predicted, actual):
#         if pred == act:
#             correct_predictions += 1
    
#     accuracy = (correct_predictions / len(predicted)) * 100
#     return accuracy

# # Example usage

# # Splitting predicted values for morning, afternoon, and evening
# morning_predictions = predicted[:10]
# afternoon_predictions = predicted[10:20]
# evening_predictions = predicted[20:30]
# # Creating combined actual values list to match the length of predicted values
# combined_actual = actual * 10  # Replicate actual values to match the predictions count
# # Combining all predictions into a single list

# # Calculating overall accuracy
# overall_accuracy = calculate_accuracy(predicted , actual)
# # Multiply by 10
# overall_accuracy *= 10
# # Round to one decimal place
# overall_accuracy = round(overall_accuracy, 1)
# print(f"Overall Predictions Accuracy: {overall_accuracy}%")


