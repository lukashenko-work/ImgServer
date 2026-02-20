"""Routes module"""

# from datetime import datetime
from flask import Flask, render_template, request, jsonify  # , url_for, redirect, send_from_directory
# from werkzeug.utils import secure_filename

from config import Config
from database import Database
from models import Image
from utils import delete_file, format_file_size, get_file_extension, is_allowed_extension, log_debug, log_error, log_success, save_file


def register_routes(app: Flask):
    """Register all routes in Flask application

    Args:
        app (_type_): _description_
    """
    @app.route(Config.ROOT_ROUTE)
    def index():
        return render_template('index.html')

    @app.route(Config.UPLOAD_ROUTE, methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            return jsonify({'error': 'File not found', 'code': 400}), 400

        file = request.files['file']
        filename = file.filename

        if not filename or filename == '':
            return jsonify({'error': 'File not found', 'code': 400}), 400

        if not is_allowed_extension(filename):
            return jsonify({'error': 'Unsupported file type', 'code': 400}), 400

        new_filename = None
        try:
            file_content = file.read()
            file_size = len(file_content)

            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size_formatted = format_file_size(Config.MAX_CONTENT_LENGTH)
                actual_size_formatted = format_file_size(file_size)
                return jsonify({'error': f'File too big ({actual_size_formatted}). Max file size {max_size_formatted}',
                                'code': 400}), 400

            success, result = save_file(filename, file_content)

            if not success:
                return jsonify({'error': f'Failed to save file ({result})', 'code': 500}), 500

            new_filename = result

            file_type = get_file_extension(filename)[1:]  # убираем точку
            image = Image(
                filename=new_filename,
                # FIXME пока не нравится как работает secure_filename
                # вместо имени файла "Взнос региональный (2).gif" вернула "2.gif"
                # original_name=secure_filename(filename),
                original_name=filename,
                size=file_size,
                file_type=file_type
            )
            success, image_id = Database.save_image(image)

            if not success:
                # Удаляем файл с диска, если не удалось сохранить в базу
                if new_filename:
                    delete_file(new_filename)
                log_error(f'Failed to save image {filename} to DB')
                return jsonify({'error': f'Failed to save image {filename} to DB', 'code': 500}), 500

            log_success(f'Image successfully saved {new_filename} to DB and folder')

            return jsonify({
                'success': True,
                'message': 'Изображение успешно загружено',
                'image': {
                    'id': image_id,
                    'filename': new_filename,
                    'original_name': file.filename,
                    'size': format_file_size(file_size),
                    'url': f'{Config.DOWNLOAD_ROUTE}/{new_filename}',
                    'delete_url': f'{Config.DELETE_ROUTE}/{image_id}'
                },
                'code': 201}), 201
        except Exception as e:
            delete_file(new_filename)
            log_error(f'Failed to load image file {e}')
            return jsonify({'error': f'Failed to save file ({e})', 'code': 500}), 500

    @app.route(Config.IMAGES_ROUTE)
    @app.route(Config.IMAGES_RANDOM_ROUTE)
    @app.route(Config.IMAGES_ROUTE + '/<int:page>')
    def list_images(page: int = 0):
        images_per_page = Config.IMAGES_PER_PAGE
        images = []
        total = -1
        if request.path.endswith(Config.IMAGES_RANDOM_ROUTE):
            images, total = Database.get_random_images()
        else:
            images, total = Database.get_paged_images(page, images_per_page)
        if total == -1:  # DB Error
            return jsonify({'error': 'Failed to load images from DB', 'code': 503}), 503
        else:
            return jsonify({
                'success': True,
                'message': 'Image list',
                'images': images,
                'total': total,
                'page': page,
                'images_per_page': images_per_page,
                'url': f'{Config.DOWNLOAD_ROUTE}/',
                'delete_url': f'{Config.DELETE_ROUTE}/',
                'code': 200}), 200

    @app.route(Config.DELETE_ROUTE + '/<int:image_id>')
    def delete_image(image_id: int):
        success, filename = Database.delete_image(image_id)

        if not success:
            log_error(f'Failed to delete image file with id: {image_id}')
            return jsonify({'error': 'Failed to delete image', 'code': 500}), 500

        delete_file(filename)

        return jsonify({
            'success': True,
            'message': 'Image deleted successfully',
            'code': 200}), 200
