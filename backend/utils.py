"""Utils module"""

import logging
import os
import typing as t
import uuid

from config import Config


# Logging
def setup_logging():
    """Настройка логирования"""
    ensure_logs_dir()
    log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    debug_level = logging.DEBUG if Config.DEBUG else logging.INFO

    logging.basicConfig(
        level=debug_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(Config.LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    log_info(f'Logging started at {Config.LOG_FILE_PATH} with level {logging.getLevelName(debug_level)}')


def log_info(message):
    """Логирует информационное сообщение"""
    logging.info(message)


def log_debug(message):
    """Логирует debug сообщение"""
    logging.debug(message)


def log_warning(message):
    """Логирует warning сообщение"""
    logging.warning(message)


def log_error(message):
    """Логирует сообщение об ошибке"""
    logging.error(message)


def log_success(message):
    """Логирует успешное действие"""
    logging.info(f'Success: {message}')


# Files and folders utils
def ensure_logs_dir():
    """Creating logs dir"""
    # FIXME почему-то любое логирование до настройки логгера ломает логирование
    # log_info('Checking/creating directories')
    os.makedirs(Config.LOGS_FOLDER, exist_ok=True)


def ensure_backups_dir():
    """Creating backups dir"""
    os.makedirs(Config.BACKUP_FOLDER, exist_ok=True)


def ensure_directories():
    """Создает необходимые папки если их нет"""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    ensure_logs_dir()
    ensure_backups_dir()


# Files validation
def get_file_extension(filename):
    """Получат расширение файла в нижнем регистре с точкой"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_extension(filename):
    """Проверяет расширение файла"""
    ext = get_file_extension(filename)
    return ext in Config.ALLOWED_EXTENSIONS


def is_valid_file_size(file_size):
    """Проверяет размер файла"""
    return 0 < file_size <= Config.MAX_CONTENT_LENGTH


def format_file_size(size_bytes: int) -> str:
    """Формирует размер файла для отображения"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.2f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.2f} MB'


def generate_unique_filename(original_filename):
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f'{unique_id}{ext}'


def validate_file(filename, file_size):
    """
    Валидирует файл по имени и размеру
    Возвращает (True, None), если валиден, иначе (False, error message)
    """
    if not is_allowed_extension(filename):
        ext = get_file_extension(filename)
        return False, f'Неподдерживаемый формат файла {ext}. Разрешены только {
            ','.join(Config.ALLOWED_EXTENSIONS)}'

    if not is_valid_file_size(file_size):
        if file_size <= 0:
            return False, 'Файл пустой'
        else:
            max_size_formatted = format_file_size(Config.MAX_CONTENT_LENGTH)
            actual_size_formatted = format_file_size(file_size)
            return False, f'Файл слишком большой {
                actual_size_formatted}. Максимальный размер файла {
                max_size_formatted}'

    return True, None


def save_file(filename: str, file_content: t.Any) -> tuple[bool, str]:
    """Сохраняет файл на диск.

    Args:
        filename (str): Оригинальное имя файла. На диск сохраняется файл с новым уникальным именем.
        file_content (t.Any): Содержимое файла

    Returns:
        tuple[bool, str]: Возвращает новое уникальное имя на диске.
    """
    try:
        # FIXME пока не нравится как работает secure_filename
        # вместо имени файла "Взнос региональный (2).gif" вернула "2.gif"
        # original_name = secure_filename(filename)
        original_name = filename
        new_filename = generate_unique_filename(original_name)
        file_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)

        log_success(f'File {new_filename} (original name: {original_name}) successfully saved to folders')
        return True, new_filename
    except Exception as e:
        error_msg = f'Ошибка сохранения файла: {e}'
        log_error(error_msg)
        return False, error_msg


def delete_file(filename):
    try:
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            log_success(f'Image {filename} deleted from folder successfully')
            return True
        return False
    except Exception as e:
        error_msg = f'Ошибка удаления файла: {e}'
        log_error(error_msg)
        return False
