from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import base64
import hashlib
import json
import os
from sql_queries import authenticate_client, insert_lecture, get_client_lecture_details

app = Flask(__name__)

# Load encryption key from JSON
App_Directory = os.path.dirname(__file__)
credentials_path = os.path.join(App_Directory, "credenials.json")

with open(credentials_path, "r") as file:
    data = json.load(file)

custom_key = data['encryptionkey']
hashed_key = hashlib.sha256(custom_key.encode()).digest()
fernet_key = base64.urlsafe_b64encode(hashed_key)
fernet = Fernet(fernet_key)

@app.route('/start_lecture', methods=['POST'])
def start_lecture():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if 'lectureId' not in data:
        return jsonify({"error": "Missing clientId or lectureId"}), 400

    encrypted_client_id = request.headers.get('Authorization')
    lecture_id = data['lectureId']

    if not encrypted_client_id or not lecture_id:
        return jsonify({"error": "Missing encrypted values"}), 400

    # Decrypt Client ID
    try:
        client_id = fernet.decrypt(encrypted_client_id.encode()).decode()
    except Exception:
        return jsonify({"error": "Invalid clientId"}), 401
    
    try:
        client_status = authenticate_client(client_id)
        if client_status["status"] == "success":
            pass
        else:
            return client_status
    except Exception as e:
        print(f"Error occured in checking client status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401
    
    try:
        lecture_status = insert_lecture(client_id, lecture_id)
        if lecture_status["message"] == "Lecture started successfully":
            pass
        else:
            return lecture_status
    except Exception as e:
        print(f"Error occured in checking lecture status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401
    
    try:
        portal_client = get_client_lecture_details(client_id, lecture_id)
        return portal_client
    except Exception as e:
        print(f"Error occured in checking lecture status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401
    
    return "ok"


if __name__ == '__main__':
    app.run(debug=True)
