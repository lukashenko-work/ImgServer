"""
Image Server App for JavaRush
"""
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import uuid
import json
from io import BytesIO

HOST = 'localhost'
PORT = 8000

IMAGE_DIR = 'images'
LOGS_DIR = 'logs'

MAX_FILE_SIZE = 5 * 1024 * 1024 #5Mb

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
ALOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif'
}

LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

def setup_logging():
    """Настройка логирования"""
    log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def log_info(message):
    """Логирует информационное сообщение"""
    logging.info(message)

def log_error(message):
    """Логирует сообщение об ошибке"""
    logging.info(message)

def log_success(message):
    """Логирует успешное действие"""
    logging.info(f'Success: {message}')


def ensure_directories():
    """Создает нелобходимые папки если их нет"""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

#Валидация файлов
def get_file_extension(filename):
    """Получат расширение файла в нижнем регистре с точкой"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_extension(filename):
    """Проверяет расширение файла"""
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS

def is_valid_file_size(file_size):
    """Проверяет размер файла"""
    return 0 < file_size <= MAX_FILE_SIZE

def format_file_size(size_bytes):
    """Формирует размер файла для отображения"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.2f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.2f} MB'

def generate_unique_filename(origina_filename):
    ext = get_file_extension(origina_filename)
    unique_id = str(uuid.uuid4())
    return f'{unique_id}{ext}'

def validate_file(filename, file_size):
    """
    Валидирует файл по имени и размеру
    Возвращает (True, None), если валиден, иначе (False, error message)
    """
    if not is_allowed_extension(filename):
        ext = get_file_extension(filename)
        return False, f'Неподдерживаемый формат файла {ext}. Разрешены только {','.join(ALLOWED_EXTENSIONS)}'

    if not is_valid_file_size(file_size):
        if file_size <= 0:
            return False, 'Файл пустой'
        else:
            max_size_formatted = format_file_size(MAX_FILE_SIZE)
            actual_size_formatted = format_file_size(file_size)
            return False, f'Файл слишком большой {actual_size_formatted}. Максимальный размер файла {max_size_formatted}'

    return True, None

#Прасинг multipart/form-data
def parse_multipart_form_data(content_type, body):
    """
    Парсит multipart/form-data и извлекает файл
    Возвращает (filename, file_content) или (None, None) при ошибке
    :param content_type: Description
    :param body: Description
    """
    try:
        if 'boundary=' not in content_type:
            return None, None
        
        boundary = content_type.split('boundary=')[1].strip()
        boundary_bytes = f'--{boundary}'.encode()

        parts = body.split(boundary_bytes)
        for part in parts:
            if b'Content-Disposition' in part:
                disposition_line = part.split(b'\r\n')[1].decode('utf-8')
                if 'filename' in disposition_line:
                    #Парсим имя файла
                    filename_start = disposition_line.find('filename="') + 10
                    filename_end = disposition_line.find('"', filename_start)
                    filename = disposition_line[filename_start:filename_end]

                    #Извлекаем содержимое файла
                    content_start = part.find(b'\r\n\r\n') + 4
                    content_end = part.rfind(b'\r\n')
                    file_content = part[content_start:content_end]

                    return filename, file_content
        return None, None
    except Exception as e:
        log_error(f'Ошибка парсинга multipart {e}')
        return None, None

def save_file(filename, file_content):
    try:
        new_filname = generate_unique_filename(filename)
        file_path = os.path.join(IMAGE_DIR, new_filname)

        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        log_success(f'Файл {new_filname} (оригинал: {filename}) сохранен')
        return True, new_filname
    except Exception as e:
        error_msg = f'Ошибка сохранения файла: {e}'
        log_error(error_msg)
        return False, error_msg


class ImageServerHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для сервера изображений"""

    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.log('Запрос главной страницы')
            self.send_welcome_page()
        else:
            self.send_error_response(404, f'Маршрут {self.path} не найден')

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_error_response(404, f'Маршрут {self.path} не найден')

    def handle_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > MAX_FILE_SIZE:
                self.log(f'Файл слишком большой: {format_file_size(content_length)}', 'error')
                self.send_error_response(
                    413,
                    f'Файл слишком большой. Максимум: {format_file_size(MAX_FILE_SIZE)}'
                )
                return
            len
            body = self.rfile.read(content_length)
            
            filename, file_content = parse_multipart_form_data(content_type, body)

            if not filename or not file_content:
                self.log('Не удалось извлечь файл из запроса', 'error')
                self.send_error_response(400, 'Файл не найден в запросе')
                return

            is_valid, error_message = validate_file(filename, len(file_content))
            if not is_valid:
                self.log(f'Файл не прошел валидацию {error_message}')
                self.send_error_response(400, error_message)
                return
            
            success, result = save_file(filename, file_content)

            if success:
                new_filename = result
                file_url = f'{IMAGE_DIR}/{new_filename}'

                self.log(f'Файл загружен: {new_filename}')

                response_data = {
                    'success': True,
                    'message': 'Файл успешно загружен',
                    'filename': new_filename,
                    'original_filename': filename,
                    'size': format_file_size(len(file_content)),
                    'url': file_url
                }
                self.send_json_response(200, response_data)
            else:
                error_msg = result
                self.log(f'Ошибка загрузки: {error_msg}')
                self.send_error_response(500, error_msg)
        except Exception as e:
            error_msg = f'Непредвиденная ошибка: {e}'
            self.log(error_msg, 'error')
            self.send_error_response(500, error_msg)


    def send_welcome_page(self):
        """Отправляет приветственное сообщение"""
        message_data = {
            'message': 'Добро пожаловать на сервер изображений',
            'endpoints': {
                'GET /': 'Эта страница',
                'POST /upload': 'Загрузка изображений'
            },
            'info': {
                'max_file_size': '5 Mb',
                'allwed_formats': list(ALLOWED_EXTENSIONS)
            }
        }
        self.send_json_response(200, message_data)

    def log(self, message, level='info'):
        """Логирует действие с информацией о запросе"""
        client_ip = self.client_address[0]
        log_message = f'{client_ip} - {self.command} - {self.path} - {message}'
        if level == 'error':
            log_error(log_message)
        else:
            log_info(log_message)

    def send_json_response(self, status_code, data):
        """Отправляет JSON ответ клиенту"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        response  = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def send_error_response(self, status_code, message):
        """Отправляет сообщение об ошибке"""
        error_data = {
            'error': message,
            'status_code': status_code
        }
        self.send_json_response(status_code, error_data)

if __name__ == '__main__':
    ensure_directories()
    setup_logging()
    server_adress = (HOST, PORT)
    httpd = HTTPServer(server_adress, ImageServerHandler)
    httpd.serve_forever()  
