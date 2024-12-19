# import mysql.connector
# from mysql.connector import Error
# from config import Config

# def create_connection():
#     """Establishes a connection to the MySQL database."""
#     try:
#         connection = mysql.connector.connect(
#             host=Config.DB_HOST,
#             user=Config.DB_USER,
#             password=Config.DB_PASSWORD,
#             database=Config.DB_NAME
#         )
#         cursor = connection.cursor()
#         cursor.execute("""
#         CREATE DATABASE IF NOT EXISTS mysql;
# """)
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS FITUSERDATA(
#                        ID INT AUTO_INCREMENT PRIMARY KEY,
#                        FIRST_NAME VARCHAR(255),
#                        LAST_NAME VARCHAR(255),
#                        EMAIL_ID VARCHAR(255),
#                        PASSWORD VARCHAR(255));
# """)    
#         connection.close()
#         cursor.close()
#         # if connection.is_connected():
#         #     print("Connection to MySQL database established.")
#         #     return connection
#     except Error as e:
#         print(f"Error while connecting to MySQL: {e}")
#         return None

# # def close_connection(connection):
# #     """Closes the database connection."""
# #     if connection.is_connected():
# #         connection.close()
# #         print("MySQL connection closed.")

# # Example usage of connection function:
# # connection = create_connection()
# # if connection:
# #     # Perform database operations
# #     close_connection(connection)


import mysql.connector
from mysql.connector import Error
from config import Config
import bcrypt

def create_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database = Config.DB_NAME,
        charset='utf8'  # Use 'utf8' character set
    )
        if connection.is_connected():
            return connection
        else:
            print("Connection failed.")
            return None
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates a new database if it doesn't exist."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME};")
        cursor.close()
    except Error as e:
        print(f"Error while creating the database: {e}")



def change_password(email, current_password, new_password):
    connection = create_connection()
    cursor = connection.cursor()
 
    cursor.execute("SELECT PASSWORD FROM FITUSERDATA WHERE EMAIL_ID = %s", (email,))
    hashed_password = cursor.fetchone()
    
    if hashed_password is None:
        return "User not found"

    if bcrypt.checkpw(current_password.encode('utf-8'), hashed_password[0].encode('utf-8')):
        
        if len(new_password) < 8:
            return "New password must be at least 8 characters long"

       
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE FITUSERDATA SET PASSWORD = %s WHERE EMAIL_ID = %s", (new_hashed_password.decode('utf-8'), email))
        connection.commit()
        
        if connection:
            cursor.close()
            connection.close()
        
        return "Password changed successfully"
    else:
        if connection:
            cursor.close()
            connection.close()
        return "Current password is incorrect"


def create_table(connection):
    """Creates a new table for user data if it doesn't exist."""
    try:
        connection.database = Config.DB_NAME  # Ensure you're using the correct database
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS FITUSERDATA(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            FIRST_NAME VARCHAR(255),
            LAST_NAME VARCHAR(255),
            EMAIL_ID VARCHAR(255),
            PASSWORD VARCHAR(255)
        );
        """)
        cursor.close()
    except Error as e:
        print(f"Error while creating the table: {e}")

def register_user(firstname, lastname, email, password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO FITUSERDATA (FIRST_NAME, LAST_NAME, EMAIL_ID, PASSWORD) VALUES (%s, %s, %s, %s)", 
                   (firstname, lastname, email, password))  # Notice VALUES and the tuple format
    connection.commit()  # Commit the transaction
    if connection:
        cursor.close()
        connection.close()


def login_user(email):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT PASSWORD FROM FITUSERDATA WHERE EMAIL_ID = %s", (email,))  # Notice the comma
    hashed_password = cursor.fetchone()
    if connection:
        cursor.close()
        connection.close()
    return hashed_password

  
def main():
    connection = create_connection()
    if connection:
        create_database(connection)
        create_table(connection)
        connection.close()

main()

# if __name__ == "__main__":
#     main()
