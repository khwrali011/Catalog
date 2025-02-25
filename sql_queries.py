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
    
def check_client(clientId, enc_client_id):
    """
        input: clientId: INT
        enc_client_id: str (Encrypted client Id)
        output: Client id decryption
    """

    # Decrypt the encypted id
    try:
        dec_client_id = fernet.decrypt(enc_client_id.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return "0"

    return "1" if clientId == dec_client_id else "0"
    
def return_client_data(clientId):
    """
        input: clientId: INT
        output: Queries on db and return client data
    """
    get_info_query = """
    SELECT 
        c.clientId,
        c.clientName,
        c.clientLicenseKey,
        c.responseAPI,
        c.lectureRouteUrl,
        c.lectureRouteUrlServer,
        c.lectureDetailUrl,
        c.isActive AS clientIsActive,
        c.createdOn AS clientCreatedOn,
        r.relationId,
        r.total_lectures,
        r.remaining_lecture,
        r.activation_date,
        r.isactive AS relationIsActive,
        r.createOn AS relationCreatedOn,
        p.packageId,
        p.packageTitle,
        p.packageDescription,
        p.packageprice,
        p.packagetypeId
    FROM rectureai.tbl_client c
    LEFT JOIN rectureai.tbl_relation_client_package r ON c.clientId = r.clientId
    LEFT JOIN rectureai.tbl_packages p ON r.packageId = p.packageId
    WHERE c.clientId = %s;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(get_info_query, (clientId,))
    
    # Fetch the first row instead of all
    row = cursor.fetchone()

    # Close connection
    cursor.close()
    conn.close()

    if row:
        return row
    else:
        return json.dumps({"error": "No data found for the given clientId"}, indent=4)
