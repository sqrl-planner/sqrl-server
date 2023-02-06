"""Application settings."""
import os

SECRET_KEY = os.getenv('SECRET_KEY')

SERVER_NAME = os.getenv('SERVER_NAME')

# MongoDB configuration
MONGODB_SETTINGS = {
    'db': os.getenv('MONGODB_DB', 'sqrl'),
    'host': os.getenv('MONGODB_HOST', 'mongodb'),
    'port': int(os.getenv('MONGODB_PORT', 27017)),
    'username': os.getenv('MONGODB_USERNAME'),
    'password': os.getenv('MONGODB_PASSWORD'),
}

GATOR_CLIENT_URL = os.getenv('GATOR_CLIENT_URL')
