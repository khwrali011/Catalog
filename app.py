from flask import Flask, request, jsonify
import json
import os
from sql_queries import authenticate_client, insert_lecture, get_client_lecture_details, generate_decryption

app = Flask(__name__)

# Load encryption key from JSON
App_Directory = os.path.dirname(__file__)
credentials_path = os.path.join(App_Directory, "credenials.json")

with open(credentials_path, "r") as file:
    data = json.load(file)

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
    
    # return str(encrypted_client_id)

    # Decrypt Client ID
    try:
        client_id = generate_decryption(str(encrypted_client_id))
    except Exception:
        return jsonify({"error": "Invalid clientId"}), 401

    # return str(client_id)
    
    try:
        client_status = authenticate_client(client_id)
        if client_status["status"] == "success":
            pass
        else:
            return client_status
    except Exception as e:
        print(f"Error occured in checking client status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401
    
    # return client_status
    
    try:
        lecture_status = insert_lecture(client_id, lecture_id)
        if lecture_status["message"] == "Lecture started successfully":
            pass
        else:
            return lecture_status
    except Exception as e:
        print(f"Error occured in checking lecture status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401
    
    # return lecture_status
    
    try:
        portal_client = get_client_lecture_details(client_id, lecture_id)
        return portal_client
    except Exception as e:
        print(f"Error occured in checking lecture status: {e}")
        return jsonify({"error": "Client authentication failed"}), 401


if __name__ == '__main__':
    app.run(debug=True)
