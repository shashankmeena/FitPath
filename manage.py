from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin


# Create a flask application
app = Flask(__name__)

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="mysql"
        )
        if connection.is_connected():
            print("Successfully connected to the database")
    except Error as e:
        print(f"Error: '{e}'")
    return connection

# Example: Fetch all users
@app.route('/users', methods=['GET'])
def get_users():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT * FROM users"
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify(result), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
	
if __name__ == '__main__':
    app.run(debug=True)



