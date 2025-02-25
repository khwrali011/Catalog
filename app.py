from flask import Flask, request, jsonify
from sql_queries import check_client, return_client_data

app = Flask(__name__)

@app.route('/get_client_detail', methods=['POST'])
def get_client_detail():
    if request.is_json:
        data = request.get_json()

        if 'clientId' not in data:
            return jsonify({"error": "Request must contain client id"}), 400
        
        client_id = data['clientId']

        if client_id.strip() == "":
            return jsonify({"error": "Client id cannot be empty"}), 400

        enc_client_id = request.headers.get('Authorization')

        # Check if Authorization header is missing or empty
        if not enc_client_id:
            return jsonify({"error": "Authorization header is missing"}), 401
        
        try:
            auth_status = check_client(client_id, enc_client_id)
            print(f"\n\nAuth Status: {auth_status}\n\n")
            if auth_status == "0":
                return jsonify({"error": "Client could not be verified"}), 400
            pass
        
        except Exception as e:
            print(f"Error in checking authentication of client: {e}")
            return jsonify({"error": "Error in client authorization"}), 400
        
        try:
            client_data = return_client_data(client_id)
            return client_data, 200
        except Exception as e:
            print(f"Error in executing qurie: {e}")
            return jsonify({"error": "Query Failed!"}), 400
        
    else:
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == '__main__':
    app.run(debug=True)
