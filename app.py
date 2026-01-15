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


class ImageServerHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для сервера изображений"""

    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.log('Запрос главной страницы')
            self.send_welcome_page()
        else:
            self.send_error_response(404, 'Маршрут не найден')

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
