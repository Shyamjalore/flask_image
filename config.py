import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/mimage_database')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
