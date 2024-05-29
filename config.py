import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://doadmin:YN46J920joD173Cn@db-mongodb-blr1-35998-4e23f427.mongo.ondigitalocean.com/admin?tls=true&authSource=admin&replicaSet=db-mongodb-blr1-35998')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
