import mysql.connector

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'rectureai'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
