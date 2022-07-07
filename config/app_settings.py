"""Application settings."""
import os


SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv(
    'SERVER_NAME', 'localhost:{0}'.format(os.getenv('PORT', '8000')))

# MongoDB configuration
MONGODB_SETTINGS = {
    'db': os.getenv('MONGODB_DB', 'sqrl'),
    'host': os.getenv('MONGODB_HOST', 'mongodb'),
    'port': int(os.getenv('MONGODB_PORT', 27017)),
    'username': os.getenv('MONGODB_USERNAME', None),
    'password': os.getenv('MONGODB_PASSWORD', None),
}

GATOR_CLIENT_URL = os.getenv('GATOR_CLIENT_URL')
