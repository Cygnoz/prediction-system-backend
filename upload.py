import pandas as pd
import pymongo
from urllib.parse import quote_plus
from collections import defaultdict
import os

# MongoDB connection details
username = "nexdeveloper1"
password = "nexdeveloper1"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xos19jy.mongodb.net/Prediction?retryWrites=true&w=majority&appName=Cluster0"

def read_xlsx(file_path):
    df = pd.read_excel(file_path)
    print(f"Columns in the file {os.path.basename(file_path)}:")
    print(df.columns.tolist())
    return df

def process_data(df):
    date_column = df.columns[0]  # 'Date'
    value_columns = df.columns[1:]  # '1:00', '6:00', '8:00'
    
    processed_data = defaultdict(lambda: {'draws': []})
    
    for _, row in df.iterrows():
        date = row[date_column]
        if pd.isna(date):
            continue  # Skip rows with missing dates
        
        month = date.strftime('%B') if isinstance(date, pd.Timestamp) else date[:7]
        year = date.year if isinstance(date, pd.Timestamp) else date.split('-')[0]
        
        draw_entry = {
            'date': date.strftime('%m/%d/%Y') if isinstance(date, pd.Timestamp) else date,
            'morning': None,
            'afternoon': None,
            'evening': None
        }
        
        for time in value_columns:
            value = row[time]
            if pd.notna(value):
                time_of_day = 'morning' if '1' in str(time) else 'afternoon' if '6' in str(time) else 'evening'
                try:
                    draw_entry[time_of_day] = float(value)
                except ValueError:
                    print(f"Warning: Could not convert value '{value}' to float for date {date} and time {time}. Skipping this entry.")
        
        processed_data[(year, month)]['draws'].append(draw_entry)
    
    return [{'year': k[0], 'month': k[1], 'draws': v['draws']} for k, v in processed_data.items()]

def setup_mongodb_collection(client, db_name, collection_name):
    db = client[db_name]
    
    schema = {
        "bsonType": "object",
        "required": ["year", "month", "draws"],
        "properties": {
            "year": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "month": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "draws": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["date", "morning", "afternoon", "evening"],
                    "properties": {
                        "date": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "morning": {
                            "bsonType": ["double","int","null"],
                            "description": "must be a double or null"
                        },
                        "afternoon": {
                            "bsonType": ["double","int", "null"],
                            "description": "must be a double or null"
                        },
                        "evening": {
                            "bsonType": ["double","int", "null"],
                            "description": "must be a double or null"
                        }
                    }
                }
            }
        }
    }
    
    if collection_name in db.list_collection_names():
        db[collection_name].drop()
    
    db.create_collection(
        collection_name,
        validator={"$jsonSchema": schema}
    )
    
    print(f"Collection '{collection_name}' created with schema validation.")
    return db[collection_name]

def upload_to_mongodb(data, collection):
    if data:
        for document in data:
            collection.update_one(
                {'year': document['year'], 'month': document['month']},
                {'$set': {'draws': document['draws']}},
                upsert=True
            )
        print(f"Uploaded {len(data)} documents to MongoDB")
    else:
        print("No valid data to upload.")

def process_folder(folder_path, client, db_name, collection_name):
    all_processed_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(folder_path, filename)
            
            print(f"\nProcessing file: {filename}")
            
            df = read_xlsx(file_path)
            processed_data = process_data(df)
            all_processed_data.extend(processed_data)
    
    # Group data by year and month
    aggregated_data = defaultdict(lambda: {'draws': []})
    for data in all_processed_data:
        key = (data['year'], data['month'])
        aggregated_data[key]['draws'].extend(data['draws'])
    
    # Convert to the format needed for MongoDB
    final_data = [{'year': k[0], 'month': k[1], 'draws': v['draws']} for k, v in aggregated_data.items()]
    
    collection = setup_mongodb_collection(client, db_name, collection_name)
    upload_to_mongodb(final_data, collection)

def main():
    folder_path = '../FINAL DATA'  # Replace with the path to your folder containing XLSX files
    db_name = 'Prediction'
    collection_name = 'AllPredictions'  # Unified collection name

    client = pymongo.MongoClient(mongodb_uri)

    process_folder(folder_path, client, db_name, collection_name)

    client.close()

if __name__ == "__main__":
    main()
