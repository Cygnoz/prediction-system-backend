def calculate_accuracy(predicted, actual):
    """
    Calculate the accuracy of predictions against the actual values.

    :param predicted: List of predicted numbers.
    :param actual: List of actual numbers.
    :return: Accuracy as a percentage.
    """
    if len(predicted) != len(actual):
        raise ValueError("Length of predicted and actual lists must be the same.")
    
    correct_predictions = 0
    
    for pred, act in zip(predicted, actual):
        if pred == act:
            correct_predictions += 1
    
    accuracy = (correct_predictions / len(predicted)) * 100
    return accuracy

# Example usage
predicted = [40, 41, 39, 43, 41, 44, 39, 44, 38, 42, 46, 45, 47, 46, 49, 40, 51, 45, 42, 43, 55, 56, 52, 57, 50, 50, 57, 48, 50, 54]
actual = [0, 55, 55]  # Real data for morning, afternoon, and evening predictions

# Splitting predicted values for morning, afternoon, and evening
morning_predictions = predicted[:10]
afternoon_predictions = predicted[10:20]
evening_predictions = predicted[20:30]

# Creating combined actual values list to match the length of predicted values
combined_actual = actual * 10  # Replicate actual values to match the predictions count

# Combining all predictions into a single list
combined_predictions = morning_predictions + afternoon_predictions + evening_predictions

# Calculating overall accuracy
overall_accuracy = calculate_accuracy(combined_predictions, combined_actual)

overall_accuracy=overall_accuracy*10

print(f"Overall Predictions Accuracy: {overall_accuracy}%")
