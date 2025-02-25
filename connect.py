import mysql.connector
from pathlib import Path
import os
import json

App_Directory = Path(__file__).parent

credentials_path = os.path.join(App_Directory, "credenials.json")

# Open and read the JSON file
with open(credentials_path, "r") as file:
    data = json.load(file)  # Parse JSON

# MySQL Database Configuration
db_config = {
    'host': data['host'],
    'user': data['user'],
    'password': data['password'],
    'database': data['database']
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
