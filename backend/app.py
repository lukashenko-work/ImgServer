"""
Image Server App for JavaRush
"""

# from http.server import HTTPServer, BaseHTTPRequestHandler
# import json
# from io import BytesIO
# import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from database import Database
from routes import register_routes
from utils import ensure_directories, log_info, setup_logging  # , log_error


# def setup_logging_():
#     """Настройка логирования"""
#     log_format = '[%(asctime)s] %(levelname)s: %(message)s'
#     date_format = '%Y-%m-%d %H:%M:%S'

#     logging.basicConfig(
#         level=logging.INFO,
#         format=log_format,
#         datefmt=date_format,
#         handlers=[
#             logging.FileHandler(Config.LOG_FILE_PATH, encoding='utf-8'),
#             logging.StreamHandler()
#         ]
#     )
#     log_info(f'Logging started at {Config.LOG_FILE_PATH}')


def create_app():
    app = Flask(__name__)
    # Settings up Flask application
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

    CORS(app)

    with app.app_context():
        ensure_directories()
        setup_logging()
        Database.init_db()

    register_routes(app)
    return app


if __name__ == '__main__':
    app = create_app()
    log_info('Image server starting')
    # app.run(host='0.0.0.0', port=8000, debug=Config.DEBUG) for Docker
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)


# Парсинг multipart/form-data
# def parse_multipart_form_data(content_type, body):
#     """
#     Парсит multipart/form-data и извлекает файл
#     Возвращает (filename, file_content) или (None, None) при ошибке
#     :param content_type: Description
#     :param body: Description
#     """
#     try:
#         if 'boundary=' not in content_type:
#             return None, None

#         boundary = content_type.split('boundary=')[1].strip()
#         boundary_bytes = f'--{boundary}'.encode()

#         parts = body.split(boundary_bytes)
#         for part in parts:
#             if b'Content-Disposition' in part:
#                 disposition_line = part.split(b'\r\n')[1].decode('utf-8')
#                 if 'filename' in disposition_line:
#                     # Парсим имя файла
#                     filename_start = disposition_line.find('filename="') + 10
#                     filename_end = disposition_line.find('"', filename_start)
#                     filename = disposition_line[filename_start:filename_end]

#                     # Извлекаем содержимое файла
#                     content_start = part.find(b'\r\n\r\n') + 4
#                     content_end = part.rfind(b'\r\n')
#                     file_content = part[content_start:content_end]

#                     return filename, file_content
#         return None, None
#     except Exception as e:
#         log_error(f'Ошибка парсинга multipart {e}')
#         return None, None


# class ImageServerHandler(BaseHTTPRequestHandler):
#     """Обработчик HTTP запросов для сервера изображений"""

#     def do_GET(self):
#         """Обработка GET запросов"""
#         if self.path == '/':
#             self.log('Запрос главной страницы')
#             self.send_welcome_page()
#         else:
#             self.send_error_response(404, f'Маршрут {self.path} не найден')

#     def do_POST(self):
#         if self.path == '/upload':
#             self.handle_upload()
#         else:
#             self.send_error_response(404, f'Маршрут {self.path} не найден')

#     def handle_upload(self):
#         try:
#             content_type = self.headers.get('Content-Type', '')
#             content_length = int(self.headers.get('Content-Length', 0))

#             if content_length > MAX_FILE_SIZE:
#                 self.log(f'Файл слишком большой: {format_file_size(content_length)}', 'error')
#                 self.send_error_response(
#                     413,
#                     f'Файл слишком большой. Максимум: {format_file_size(MAX_FILE_SIZE)}'
#                 )
#                 return

#             body = self.rfile.read(content_length)

#             filename, file_content = parse_multipart_form_data(content_type, body)

#             if not filename or not file_content:
#                 self.log('Не удалось извлечь файл из запроса', 'error')
#                 self.send_error_response(400, 'Файл не найден в запросе')
#                 return

#             is_valid, error_message = validate_file(filename, len(file_content))
#             if not is_valid:
#                 self.log(f'Файл не прошел валидацию {error_message}')
#                 self.send_error_response(400, error_message)
#                 return

#             success, result = save_file(filename, file_content)

#             if success:
#                 new_filename = result
#                 file_url = f'{IMAGE_DIR}/{new_filename}'

#                 self.log(f'Файл загружен: {new_filename}')

#                 response_data = {
#                     'success': True,
#                     'message': 'Файл успешно загружен',
#                     'filename': new_filename,
#                     'original_filename': filename,
#                     'size': format_file_size(len(file_content)),
#                     'url': file_url
#                 }
#                 self.send_json_response(200, response_data)
#             else:
#                 error_msg = result
#                 self.log(f'Ошибка загрузки: {error_msg}')
#                 self.send_error_response(500, error_msg)
#         except Exception as e:
#             error_msg = f'Непредвиденная ошибка: {e}'
#             self.log(error_msg, 'error')
#             self.send_error_response(500, error_msg)

#     def send_welcome_page(self):
#         """Отправляет приветственное сообщение"""
#         message_data = {
#             'message': 'Добро пожаловать на сервер изображений',
#             'endpoints': {
#                 'GET /': 'Эта страница',
#                 'POST /upload': 'Загрузка изображений'
#             },
#             'info': {
#                 'max_file_size': '5 Mb',
#                 'allowed_formats': list(ALLOWED_EXTENSIONS)
#             }
#         }
#         self.send_json_response(200, message_data)

#     def log(self, message, level='info'):
#         """Логирует действие с информацией о запросе"""
#         client_ip = self.client_address[0]
#         log_message = f'{client_ip} - {self.command} - {self.path} - {message}'
#         if level == 'error':
#             log_error(log_message)
#         else:
#             log_info(log_message)

#     def send_json_response(self, status_code, data):
#         """Отправляет JSON ответ клиенту"""
#         self.send_response(status_code)
#         self.send_header('Content-Type', 'application/json; charset=utf-8')
#         self.end_headers()

#         response  = json.dumps(data, ensure_ascii=False, indent=2)
#         self.wfile.write(response.encode('utf-8'))

#     def send_error_response(self, status_code, message):
#         """Отправляет сообщение об ошибке"""
#         error_data = {
#             'error': message,
#             'status_code': status_code
#         }
#         self.send_json_response(status_code, error_data)


# if __name__ == '__main__':
#     ensure_directories()
#     setup_logging()
#     server_address = (HOST, PORT)
#     httpd = HTTPServer(server_address, ImageServerHandler)
#     httpd.serve_forever()
