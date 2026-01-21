""" Environment variables module """

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DEBUG = bool(os.getenv('DEBUG', 'True'))

    # Directories
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'images')

    # Web routes
    ROOT_ROUTE = '/'
    UPLOAD_ROUTE = ROOT_ROUTE + 'upload'
    DELETE_ROUTE = ROOT_ROUTE + 'delete'
    IMAGES_ROUTE = ROOT_ROUTE + 'images'

    # Max image file size
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5Mb

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    ALOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif'
    }

    # Server settings
    HOST = 'localhost'
    PORT = 8000

    # Logging settings
    LOGS_FOLDER = os.getenv('LOGS_FOLDER', 'logs')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_FILE_PATH = os.path.join(LOGS_FOLDER, LOG_FILE)

    # DB Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgersql://postgres:password@localhost:5432/images_db')

    # Pagination
    ITEMS_PER_PAGE = 10

    # Backups settings
    BACKUP_FOLDER = 'backup'
