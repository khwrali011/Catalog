import json
from connect import get_db_connection
# from cryptography.fernet import Fernet
from Cryptodome.Cipher import AES
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

# Generate a 32-byte key using SHA-256
hashed_key = hashlib.sha256(custom_key.encode()).digest()

# Use a fixed IV (MUST be 16 bytes)
iv = b'0123456789abcdef'

# Pad client_id to be multiple of 16 bytes
def pad(data):
    return data + (16 - len(data) % 16) * chr(16 - len(data) % 16)

def unpad(data):
    return data[:-ord(data[-1])]

def generate_encryption(input):
    cipher = AES.new(hashed_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(input).encode())
    enc_input = base64.b64encode(encrypted).decode()
    return enc_input

def generate_decryption(input):
    cipher = AES.new(hashed_key, AES.MODE_CBC, iv)
    decrypted_input = unpad(cipher.decrypt(base64.b64decode(input)).decode())
    return decrypted_input

# print(generate_decryption("B2O01IfDnTo8hiSSTUJSag=="))

def delete_lectures_by_client(client_id):
    """
    Delete all lectures associated with the given client ID.
    """
    query_check_client = "SELECT COUNT(*) FROM tbl_client WHERE clientId = %s"
    query_check_lectures = "SELECT COUNT(*) FROM lectures WHERE client_id = %s"
    query_delete = "DELETE FROM lectures WHERE client_id = %s"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if client exists
    cursor.execute(query_check_client, (client_id,))
    client_exists = cursor.fetchone()[0]

    if client_exists == 0:
        cursor.close()
        conn.close()
        return {"status": "error", "message": f"Client ID {client_id} does not exist."}

    # Check if client has any lectures
    cursor.execute(query_check_lectures, (client_id,))
    lecture_count = cursor.fetchone()[0]

    if lecture_count == 0:
        cursor.close()
        conn.close()
        return {"status": "error", "message": f"No lectures found for Client ID {client_id}."}

    # Delete lectures
    try:
        cursor.execute(query_delete, (client_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": f"Deleted {lecture_count} lecture(s) for Client ID {client_id}."}
    except Exception as e:
        cursor.close()
        conn.close()
        return {"status": "error", "message": str(e)}



# Function to update ngrok URL for a specific client
def update_ngrok_url(client_id, ngrok_url):
    """
    Update the lectureRouteUrl field for a specific client
    """
    # Check if the client exists
    query_check = "SELECT COUNT(*) FROM tbl_client WHERE clientId = %s"
    query_update = "UPDATE tbl_client SET lectureRouteUrl = %s WHERE clientId = %s"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if client exists
    cursor.execute(query_check, (client_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.close()
        conn.close()
        return {"status": "error", "message": f"Client ID {client_id} not found"}
    
    # Update the ngrok URL
    try:
        cursor.execute(query_update, (ngrok_url, client_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Ngrok URL updated successfully"}
    except Exception as e:
        cursor.close()
        conn.close()
        return {"status": "error", "message": f"Error updating Ngrok URL: {str(e)}"}

# Function to validate user credentials
def validate_user(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM credentials WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Check if user exists and password matches
        if user and user["password"] == password:
            return True
    return False

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
    expire_check = f"SELECT is_expired FROM lectures WHERE lecture_id = {lecture_id}"
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

        # Check for existing lecture
        cursor.execute(expire_check)
        expired = cursor.fetchone()[0]
        expired = str(expired)
        print(f"Count: {expired}")

        if expired == "1":
            cursor.close()
            conn.close()
            return {"message": "Lecture has been recorded!"}
        
        cursor.close()
        conn.close()
        return {"message": "Lecture started successfully"}

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
    
    # return result

    # Encrypt the required fields
    encrypted_data = {
        "isActive": result["isActive"],  # No encryption for isActive
        "lectureRouteUrl": result["lectureRouteUrl"]  # No encryption for lectureRouteUrl
    }

    return encrypted_data

def mark_lecture_expired(client_id, lecture_id):
    """
    Marks the lecture as expired by setting isExpired to True.
    """
    # query = """
    # UPDATE lectures
    # SET is_expired = TRUE
    # WHERE client_id = %s AND lecture_id = %s;
    # """
    query = """
    UPDATE lectures
    SET is_expired = TRUE, lecture_end_date = NOW()
    WHERE client_id = %s AND lecture_id = %s;
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(query, (client_id, lecture_id))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"message": "Lecture ended successfully"}

def check_lecture_expiry(lecture_id):
    """
    Check if the lecture is expired or not.
    """
    query = f"""
    SELECT is_expired FROM lectures WHERE lecture_id = {lecture_id};
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    # print(f"Result: {type(result)}")
    status = str(result[0])
    # print(f"Status: {type(status)}")
    return status

def get_client(client_id):
    """
    Get Client Info from db.
    """
    query = f"""
    SELECT * FROM tbl_client WHERE clientId = {client_id};
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    print(f"Result: {result}")
    return result

def get_client_relational_object(client_id):
    """
    Get relational client object
    """
    query = f"""
    SELECT 
        c.clientId,
        c.clientName,
        c.clientLicenseKey,
        c.responseAPI,
        c.lectureRouteUrl,
        c.lectureRouteUrlServer,
        c.isActive AS clientIsActive,
        c.createdOn AS clientCreatedOn,
        c.client_auth,
        c.lectureDetailUrl,
        r.relationId,
        r.packageId,
        r.activation_date,
        r.isactive AS relationIsActive,
        r.createOn AS relationCreatedOn,
        r.currency
    FROM 
        tbl_client c
    LEFT JOIN 
        tbl_relation_client_package r 
    ON 
        c.clientId = r.clientId
    WHERE 
        c.clientId = {client_id};
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    print(f"Result: {result}")
    return result