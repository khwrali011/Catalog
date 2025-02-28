import json
from connect import get_db_connection
from cryptography.fernet import Fernet
import base64
import hashlib
from pathlib import Path
import os

App_Directory = Path(__file__).parent

credentials_path = os.path.join(App_Directory, "credenials.json")

# Open and read the JSON file
with open(credentials_path, "r") as file:
    data = json.load(file)  # Parse JSON

# Custom key 
custom_key = data['encryptionkey']

# Derive a 32-byte key using SHA256 and then base64 encode it
hashed_key = hashlib.sha256(custom_key.encode()).digest()
fernet_key = base64.urlsafe_b64encode(hashed_key)

# Initialize Fernet with the derived key
fernet = Fernet(fernet_key)

def authenticate_client(client_id):
    """
    Authenticate the client by checking if clientId exists and is active.
    """
    query = """
    SELECT clientId, client_auth, isActive 
    FROM tbl_client 
    WHERE clientId = %s AND isActive = 1;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(query, (client_id,))
    client_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if client_data:
        return {"status": "success", "clientId": client_data["clientId"]}
    else:
        return {"status": "error", "message": "Client authentication failed or inactive"}
    
def insert_lecture(client_id, lecture_id):
    """
    Insert a new lecture record into the lectures table.
    Ensures that duplicate lectures are not inserted.
    """
    query_check = "SELECT COUNT(*) FROM lectures WHERE client_id = %s AND lecture_id = %s"
    query_insert = """
    INSERT INTO lectures (client_id, lecture_id, lecture_start_date) 
    VALUES (%s, %s, NOW())
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing lecture
    cursor.execute(query_check, (client_id, lecture_id))
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.close()
        conn.close()
        return {"message": "Lecture already recorded"}

    # Insert new lecture
    cursor.execute(query_insert, (client_id, lecture_id))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"message": "Lecture started successfully"}

def get_client_lecture_details(client_id, lecture_id):
    """
    Fetch client and lecture details from DB, then encrypt sensitive fields.
    """
    query = """
    SELECT 
        tbl_client.clientId,
        tbl_client.responseAPI,
        tbl_client.isActive,
        tbl_client.lectureRouteUrl
    FROM 
        tbl_client
    WHERE 
        clientId = %s;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(query, (client_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return {"error": "No records found for the given clientId"}

    # Encrypt the required fields
    encrypted_data = {
        "encrypted_client_id": fernet.encrypt(str(result["clientId"]).encode()).decode(),
        "encrypted_lecture_id": fernet.encrypt(lecture_id.encode()).decode(),
        "encrypted_responseAPI": fernet.encrypt(result["responseAPI"].encode()).decode(),
        "isActive": result["isActive"],  # No encryption for isActive
        "lectureRouteUrl": result["lectureRouteUrl"]  # No encryption for lectureRouteUrl
    }

    return encrypted_data
