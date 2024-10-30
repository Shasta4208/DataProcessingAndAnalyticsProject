import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta
import schedule
import time

DB_USER = 'postgres'
DB_PASSWORD = 'Shasta42'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'NodeOut'

csv_directory = r'C:\Users\larso\OneDrive\Documents\Project\NodeOutput'
connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(connection_string)

try:
    with engine.connect() as connection:
        print("Connection to the PostgreSQL database established successfully.")
except Exception as e:
    print(f"Connection failed: {e}")
    
def process_new_csv_files():
    start_time = time.time()
    now = datetime.now()
    time_threshold = now - timedelta(days=1)
    
    for filename in os.listdir(csv_directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_directory, filename)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time > time_threshold:
                df = pd.read_csv(file_path)
                table_name = os.path.splitext(filename)[0]
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                print(f"Data from {filename} has been successfully inserted into table '{table_name}'.")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken for this run: {duration:.2f} seconds")
schedule.every(2).minutes.do(process_new_csv_files)

while True:
    schedule.run_pending()
    time.sleep(2)  
