"""Application settings."""
import os
from sqrl.data.sources import utsg as utsg_source


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

# Dataset sources
# TODO: Make this controllable via environment variables
DATASET_SOURCES = {
    'utsg-timetable': utsg_source.UTSG_ArtsSci_TimetableDatasetSource(
        session=None),
}
