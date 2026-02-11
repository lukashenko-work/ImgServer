""" Environment variables module """

import os
from dotenv import load_dotenv

load_dotenv()


def split_env_var_to_set(env_str: str | None) -> set[str]:
    """Convert environment variable string to set

    Args:
        env_str (str): Environment variable string

    Returns:
        set[str]: Set of strings or empty set
    """

    if env_str:
        # Split the string and create a set to store unique values
        # Strip whitespace from each value if necessary
        result = set(value.strip() for value in env_str.split(','))
    else:
        # Default to an empty set if the env var is not set
        result = set()
    return result


def get_int_env_var(key: str, default: int) -> int:
    """Retrieves an environment variable as an integer.

    Args:
        key (str): Environment variable key
        default (int | None, optional): Default value, optional. Defaults to None.

    Returns:
        int | None: Returns the default value if the variable is missing or invalid
    """

    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        # вызывает циклическую ссылку
        # log_warning(f"Warning: Environment variable '{key}' is not a valid integer. Using default value.")
        return default


class Config:
    """Config class contains application settings
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DEBUG = bool(os.getenv('DEBUG', 'True'))

    # Directories
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'images')

    # Web routes
    ROOT_ROUTE = os.getenv('ROOT_ROUTE', '/api/')
    UPLOAD_ROUTE = ROOT_ROUTE + os.getenv('UPLOAD_ROUTE', 'upload')
    DELETE_ROUTE = ROOT_ROUTE + os.getenv('DELETE_ROUTE', 'delete')
    IMAGES_ROUTE = ROOT_ROUTE + os.getenv('IMAGES_ROUTE', 'images')

    # Images constraints
    # Max image file size
    MAX_CONTENT_LENGTH = get_int_env_var('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)  # 5Mb
    if not MAX_CONTENT_LENGTH:
        MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Images extensions
    var_string = os.getenv('ALLOWED_EXTENSIONS')
    ALLOWED_EXTENSIONS = split_env_var_to_set(var_string)

    if not ALLOWED_EXTENSIONS:
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

    # Images MIME types
    var_string = os.getenv('ALLOWED_MIME_TYPES')
    ALLOWED_MIME_TYPES = split_env_var_to_set(var_string)

    if not ALLOWED_MIME_TYPES:
        ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
    FLASK_PORT = get_int_env_var('FLASK_PORT', 8000)
    FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG', 'True'))

    # Logging settings
    LOGS_FOLDER = os.getenv('LOGS_FOLDER', 'logs')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_FILE_PATH = os.path.join(LOGS_FOLDER, LOG_FILE)

    # DB Settings
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Pagination
    IMAGES_PER_PAGE = get_int_env_var('IMAGES_PER_PAGE', 10)

    # Backups settings
    BACKUP_FOLDER = os.getenv('BACKUP_FOLDER', 'backup')
    BACKUP_TIMESTAMP_FORMAT = os.getenv('BACKUP_TIMESTAMP_FORMAT', '%Y_%m_%d_%H_%M_%S')
