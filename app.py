from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from groq import Groq
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from database import create_connection, register_user,login_user,main
from mysql.connector import Error
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# Configuration for JWT
app.config['JWT_SECRET_KEY'] = 'sachin12345'  # Change this to a strong secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)
jwt = JWTManager(app)

# In-memory user store for demonstration
# In a real app, you should use a database
# users = {}

# def create_connection():
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",  # Your MySQL server address (or "127.0.0.1")
#             user="root",  # Your MySQL username
#             password="root",  # Your MySQL password
#             database="mysql"  # The name of the database you want to connect to
#         )
#         if connection.is_connected():
#             print("Successfully connected to the database")
#     except Error as e:
#         print(f"Error: '{e}'")
#     return connection

# Example: Connect to MySQL
# conn = create_connection()

# # Don't forget to close the connection when you're done
# if conn and conn.is_connected():
#     conn.close()

# def insert_user(connection, username, fullname, gmail, password):
#     cursor = connection.cursor()
#     try:
#         query = """INSERT INTO users (username, fullname, gmail, password)
#                    VALUES (%s, %s, %s, %s)"""
#         values = (username, fullname, gmail, password)
#         cursor.execute(query, values)
#         connection.commit()
#         print("User inserted successfully")
#     except Error as e:
#         print(f"Error: '{e}'")


api_key = os.getenv("GROQ_API_KEY")
# print(api_key)

def generate_ai_response(height, weight, age, gender, aim, diet):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are an advanced AI fitness coach responsible for giving diet and fitness plans based on height, weight, age, gender, aim (gain, lose, or maintain) and diet (vegetarian and non-vegetarian)."
            },
            {
                "role": "user",
                "content": f"Height: {height}\nWeight: {weight}\nAge: {age}\Gender: {gender}\nAim: {aim}\nDiet: {diet}"
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response = completion.choices[0].message.content
    return response

def generate_chatbot_response(question):
   
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    if not api_key:
        return "Error: API key for Groq not found."
    
    try:        
        completion = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[
                {
                    "role": "system",
                    "content": "You are an advanced AI fitness coach responsible for answering user's fitness-related questions."
                },
                {
                    "role": "user",
                    "content": f"Question: {question}"
                }
            ],
            temperature=1,  # Adjust temperature for more creative or focused responses
            max_tokens=1024,  # Define how long the response can be
            top_p=1,  # Use nucleus sampling (top_p) for better response variety
            stream=False,  # Disable streaming for synchronous response
            stop=None,  # No specific stop sequence
        )

        # Extract the chatbot's response
        response = completion.choices[0].message.content

    except Exception as e:
        # Handle any exceptions (e.g., network issues, API errors)
        return f"Error generating chatbot response: {str(e)}"
    
    return response

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get the data from the form
        firstname = request.form.get('firstname', '')
        lastname = request.form.get('lastname', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Check if all fields are provided
        if not firstname or not lastname or not email or not password or not confirm_password:
            return jsonify({"message": "All fields are required"}), 400
        
        if password != confirm_password:
            return jsonify({"message":"Passwords do not match."}), 400
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Register the user in the database
        register_user(firstname, lastname, email, hashed_password)
        
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Error during registration: {str(e)}"}), 500


# @app.route('/register', methods=['POST'])
# def register():
#     try:
#         # Get the data from the form
#         firstname = request.form.get('firstname', '')
#         lastname = request.form.get('lastname', '')
#         email = request.form.get('email', '')
#         password = request.form.get('password', '')
#         confirm_password = request.form.get('confirm_password', '')

#         # Check if all fields are provided
#         if not firstname or not lastname or not email or not password or not confirm_password:
#             return jsonify({"message": "All fields are required"}), 400
        
#         if password != confirm_password:
#             return jsonify({"message":"Please Check password you entered."})
        
#         hashed_password = generate_password_hash(password)
        
#         register_user(firstname,lastname,email,hashed_password)
  
    # # Check if the email is already registered (optional, if you want to enforce unique emails)
    # for user_data in users.values():
    #     if user_data['gmail'] == gmail:
    #         return jsonify({"message": "Gmail is already registered"}), 400

    # # Check if passwords match
    # if password != confirm_password:
    #     return jsonify({"message": "Passwords do not match"}), 400

    # # Hash the password for secure storage
    # hashed_password = generate_password_hash(password)
    
    # # Store the user's data
    # users[username] = {
    #     'fullname': fullname,
    #     'gmail': gmail,
    #     'password': hashed_password
    # }
    
    #     return jsonify({"message": "User registered successfully"}), 201
    # except Exception as e:
    #     return jsonify({"error":f"Error Occured during Register.{str(e)}"})

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '')
    password = request.form.get('password', '')

    if not email or not password:
        return jsonify({"message": "Please enter both email and password."}), 401

    hashed_password = login_user(email)
    
    if hashed_password:
        
        if not check_password_hash(hashed_password[0], password):
            return jsonify({"message": "Invalid password."}), 401
        else:
            access_token = create_access_token(identity=email)
            return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else: 
        return jsonify({"message": "User not registered."}), 403
    
@app.route('/change-password', methods=['POST'])
@jwt_required()  
def change_password():
    
    email = get_jwt_identity()
    
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({"message": "Please enter both current and new passwords."}), 400

    hashed_password = login_user(email)
    
    if hashed_password:
        
        if not check_password_hash(hashed_password[0], current_password):
            return jsonify({"message": "Current password is incorrect."}), 401

        if len(new_password) < 8:
            return jsonify({"message": "New password must be at least 8 characters long."}), 400

        new_hashed_password = generate_password_hash(new_password)

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE FITUSERDATA SET PASSWORD = %s WHERE EMAIL_ID = %s", (new_hashed_password, email))
        connection.commit()

        if connection:
            cursor.close()
            connection.close()

        return jsonify({"message": "Password changed successfully."}), 200
    else:
        return jsonify({"message": "User not registered."}), 403


# @app.route('/login', methods=['POST'])
# def login():
#     email = request.form.get('email', '')
#     password = request.form.get('password', '')

#     # user = users.get(username)
#     # if not email or not check_password_hash(user['password'], password):
#     #     return jsonify({"message": "Invalid username or password"}), 401
#     if not email or not password:
#         return jsonify({"message":"Please enter Email and Password."}),401
    
#     hashed_password = login_user(email)
#     if hashed_password:
#         if not check_password_hash(hashed_password[0],password):
#             return jsonify({"message":"Please enter valid password."}),401
#         else:
#             return jsonify({"message":"Login Successfull."}),200
#     else: 
#         return jsonify({"message":"Please Register Your Details."}), 403

    # # Create a new access token
    # access_token = create_access_token(identity=username)

    # # Return user data along with the access token
    # user_data = {
    #     "username": username,
    #     "fullname": user.get('fullname'),
    #     "gmail": user.get('gmail'),
    #     "access_token": access_token
    # }

    # return jsonify(user_data), 200


@app.route('/ask_question', methods=['POST'])
@jwt_required() 
def generate_response():
    current_user = get_jwt_identity()  
    height = request.form.get('height', '')
    weight = request.form.get('weight', '')
    age = request.form.get('age', '')
    gender = request.form.get('gender', '')
    aim = request.form.get('aim', '')
    diet = request.form.get('diet', '')

    response = generate_ai_response(height, weight, age, gender, aim, diet)
    return jsonify({"response": response, "user": current_user})


@app.route('/ask_chatbot', methods=['POST'])
@jwt_required() 
def generate_chatbot():
    try:
       
        current_user = get_jwt_identity()

        question = request.form.get('question', '').strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        response = generate_chatbot_response(question)

        return jsonify({"response": response, "user": current_user})

    except Exception as e:
      
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    main()
    app.run(debug=False, threaded=True)
