from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import json
import os
from sql_queries import authenticate_client, insert_lecture, get_client_lecture_details, generate_decryption
from sql_queries import mark_lecture_expired, check_lecture_expiry, get_client_relational_object, validate_user 
from sql_queries import update_ngrok_url, delete_lectures_by_client, delete_specific_lecture_func, get_lectures_count
from sql_queries import get_lecture_start_status, insert_client, insert_client_contact_info  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some secret key'

# Load encryption key from JSON
App_Directory = os.path.dirname(__file__)
credentials_path = os.path.join(App_Directory, "credenials.json")

with open(credentials_path, "r") as file:
    data = json.load(file)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if validate_user(username, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        client_name = request.form.get('client_name')
        number = request.form.get('number') or None
        email = request.form.get('email') or None
        address = request.form.get('address') or None

        if not client_name:
            return render_template('add_client.html', error="Client name is required.")

        try:
            client_id = insert_client(client_name)  # Insert client into DB
            if client_id:
                session['client_id'] = client_id  # Store client ID in session

                # Insert contact details in the same step
                insert_client_contact_info(client_id, number, email, address)

                return render_template('add_client.html', 
                                       success=f"Client created successfully with ID: {client_id} and contact info added.")
            else:
                return render_template('add_client.html', error="Failed to create client.")
        except Exception as e:
            return render_template('add_client.html', error=f"Error: {str(e)}")

    return render_template('add_client.html')

@app.route('/update_ngrok', methods=['GET', 'POST'])
def update_ngrok():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        client_id = request.form['client_id']
        ngrok_url = request.form['ngrok_url']
        
        # Validate inputs
        if not client_id or not ngrok_url:
            return render_template('update_ngrok.html', error="Both Client ID and Ngrok URL are required")
        
        try:
            # Attempt to convert client_id to integer
            client_id = int(client_id)
        except ValueError:
            return render_template('update_ngrok.html', error="Client ID must be a number")
        
        # Update the URL in the database
        result = update_ngrok_url(client_id, ngrok_url)
        
        if result.get('status') == 'success':
            return render_template('update_ngrok.html', success=f"Ngrok URL updated successfully for client {client_id}")
        else:
            return render_template('update_ngrok.html', error=result.get('message', "Failed to update Ngrok URL"))
    
    return render_template('update_ngrok.html')

@app.route('/delete_lectures')
def delete_lectures():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('delete_lectures.html')

@app.route('/process_delete_lectures', methods=['POST'])
def process_delete_lectures():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    client_id = request.form.get('client_id')

    if not client_id.isdigit():
        return render_template('delete_lectures.html', error="Client ID must be a number")

    client_id = int(client_id)
    
    result = delete_lectures_by_client(client_id)

    if result["status"] == "success":
        return render_template('delete_lectures.html', success=result["message"])
    else:
        return render_template('delete_lectures.html', error=result["message"])
    
@app.route('/delete_specific_lecture')
def delete_specific_lecture():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('delete_specific_lecture.html')

@app.route('/process_delete_specific_lecture', methods=['POST'])
def process_delete_specific_lecture():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    client_id = request.form.get('client_id')
    lecture_id = request.form.get('lecture_id')

    if not client_id.isdigit() or not lecture_id.isdigit():
        return render_template('delete_specific_lecture.html', error="Client ID and Lecture ID must be numbers.")

    client_id, lecture_id = int(client_id), int(lecture_id)

    result = delete_specific_lecture_func(client_id, lecture_id)

    if result["status"] == "success":
        return render_template('delete_specific_lecture.html', success=result["message"])
    else:
        return render_template('delete_specific_lecture.html', error=result["message"])

@app.route('/start_lecture', methods=['POST'])
def start_lecture():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if 'lectureId' not in data:
        return jsonify({"error": "Missing clientId or lectureId"}), 400

    encrypted_client_id = data['key']
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
        # return lecture_status
        if lecture_status["message"] == "Lecture started successfully":
            pass
        elif lecture_status["message"] == "Lecture has been recorded!":
            print("ok")
            return lecture_status, 200
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

@app.route('/end_lecture', methods=['POST'])
def end_lecture():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if 'lecture_Id' not in data:
        return jsonify({"error": "Missing clientId or lectureId"}), 400

    encrypted_client_id = request.headers.get('Authorization')
    lecture_id = data.get('lecture_Id')

    if not encrypted_client_id or not lecture_id:
        return jsonify({"error": "Missing values"}), 400

    # Decrypt values
    try:
        client_id = generate_decryption(encrypted_client_id)
    except Exception:
        return jsonify({"error": "Invalid encrypted data"}), 401

    # Mark lecture as expired
    update_status = mark_lecture_expired(client_id, lecture_id)
    return jsonify(update_status)

@app.route('/get_client_info', methods=['POST'])
def get_client_info():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if 'lecture_Id' not in data:
        return jsonify({"error": "Missing clientId or lectureId"}), 400

    encrypted_client_id = request.headers.get('Authorization')
    lecture_id = data.get('lecture_Id')
    if not encrypted_client_id or not lecture_id:
        return jsonify({"error": "Missing values"}), 400

    # Decrypt values
    try:
        client_id = generate_decryption(encrypted_client_id)
    except Exception:
        return jsonify({"error": "Invalid encrypted data"}), 401
    
    try:
        client_object = get_client_relational_object(client_id)
        # return client_object

    except Exception as e:
        print(f"Error getting client info: {e}")
        return jsonify({"error": "Client Retrieval Failed!"}), 401
    
    try:
        lecture_status = check_lecture_expiry(lecture_id)
        # print(f"Lecture Status: {lecture_status}")
        # return lecture_status
        lecture_status = str(lecture_status)
        if lecture_status == "1":
            client_object["is_expired"] = "1"
        else:
            client_object["is_expired"] = "0"
        
        return client_object, 200
    
    except Exception as e:
        print(f"Error Occured in checking lecture status: {e}")
        return jsonify({"error": "Lecture Validation Failed!"}), 401
    
@app.route('/get_client_information', methods=['POST'])
def get_client_information():
    try:
        if not request.is_json:
            return jsonify({"errorCode": "003", "message": "Request must be JSON"}), 400

        data = request.get_json()

        if 'lecture_Id' not in data or 'Authorization' not in request.headers:
            return jsonify({"errorCode": "003", "message": "Missing clientId or lectureId"}), 400
        
        encrypted_client_id = request.headers.get('Authorization')
        lecture_id = data.get('lecture_Id')

        # Decrypt client ID
        try:
            client_id = generate_decryption(encrypted_client_id)
            # return client_id
        except Exception:
            return jsonify({"errorCode": "003", "message": "Invalid client ID"}), 401

        status = get_lecture_start_status(client_id, lecture_id)
        if not status:
            return jsonify({"errorCode": "003", "message": "Cannot record this lecture because portal has not started this"}), 400

        # Get client object
        try:
            client_object = get_client_relational_object(client_id)
            # return client_object
            if not client_object:
                return jsonify({"errorCode": "003", "message": "Client not found"}), 404
        except Exception as e:
            return jsonify({"errorCode": "003", "message": f"Error retrieving client: {str(e)}"}), 500

        # Check if client is demoClient
        if client_object.get("isDemoClient") == 1:

            lecture_count = get_lectures_count(client_id)
            # return str(lecture_count)

            demoLectures = client_object.get("demoLectures", 0)
            if lecture_count > demoLectures:
                return jsonify({"errorCode": "004", "message": "Lecture quota exceeded! Please contact vendor"}), 403
        
        # return client_object
        
        # Check if lecture is expired
        try:
            lecture_status = check_lecture_expiry(lecture_id)
            if str(lecture_status) == "1":
                return jsonify({"errorCode": "005", "message": "Lecture has been recorded!"}), 200
        except Exception as e:
            return jsonify({"errorCode": "003", "message": f"Error checking lecture expiry: {str(e)}"}), 500

        # Success response
        return jsonify({"errorCode": "001", "message": "Client is available!", "client": client_object}), 200

    except Exception as e:
        return jsonify({"errorCode": "003", "message": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
