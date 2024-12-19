import os

class Config:
    # General Configurations
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Default if not set in .env

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')  # Host for the MySQL database
    DB_USER = os.getenv('DB_USER', 'root')  # MySQL username
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')  # MySQL password
    DB_NAME = os.getenv('DB_NAME', 'mysql')  # Database name
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable Flask-SQLAlchemy modification notifications

    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Groq API key

    # Other configurations like JWT, etc., can go here
