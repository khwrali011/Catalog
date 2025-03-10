from connect import get_db_connection

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