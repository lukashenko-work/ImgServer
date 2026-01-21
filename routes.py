"""Routes module"""

from datetime import datetime
from flask import render_template, request, jsonify, url_for  # , redirect, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from database import Database
from models import Image
from utils import delete_file, format_file_size, get_file_extension, is_allowed_extension, log_error, log_success, save_file


def register_routes(app):
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
            return jsonify({'error': 'File not found'}, 400)
        
        file = request.files['file']
        filename = file.filename
        
        if not filename or filename == '':
            return jsonify({'error': 'File not found'}, 400)

        if not is_allowed_extension(filename):
            return jsonify({'error': 'Unsupported fyile type'}, 400)

        try:
            file_content = file.read()
            file_size = len(file_content)

            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size_formatted = format_file_size(Config.MAX_CONTENT_LENGTH)
                actual_size_formatted = format_file_size(file_size)
                return jsonify({'error': f'File too big ({actual_size_formatted}). Max file size {max_size_formatted}'},
                               400)

            success, result = save_file(filename, file_content)

            if not success:
                return jsonify({'error': f'Failed to save file ({result})'}, 500)

            new_filename = result

            file_type = get_file_extension(filename)[1:] # убираем точку
            image = Image(
                filename=new_filename,
                original_name=secure_filename(filename),
                size=file_size,
                file_type=file_type
            )
            # TODO разкомменировать для сохранения в DB
            success, image_id = True, 1
            # success, image_id = Database.save_image(image)

            if not success:
                delete_file(new_filename)
                return jsonify({'error': f'Failed to save image {filename} to DB)'}, 500)

            log_success(f'Image succeesfully saved {new_filename}')

            return jsonify({
                'success': True,
                'message': 'Изображение успешно загружено',
                'image': {
                    'id': image_id,
                    'filename': new_filename,
                    'original_name': file.filename,
                    'size': format_file_size(file_size),
                    'url': f'/{Config.UPLOAD_FOLDER}/{new_filename}',
                    'delete_url': f'{Config.DELETE_ROUTE}/{image_id}'
                },
            }, 201)
        except Exception as e:
            # TODO разкомменировать для удаления в случае ошибки
            # delete_file(new_fileName)
            log_error(f'Failed to load image file {e}')
            return jsonify({'error': f'Failed to save file ({e})'}, 500)

    @app.route(Config.IMAGES_ROUTE)
    def list_images():
        images = Database.get_images()
        return jsonify({
            'success': True,
            'message': 'Image list will be here)',
            'images': images
            }, 200)

    @app.route(Config.DELETE_ROUTE + '/<int:image_id>')
    def delete_image(image_id: int):
        # TODO разкомменировать для удаления из DB
        success, filename = True, '623530da-6c14-43c4-9d5e-d38d267c802d.jpg'
        # success, filename = Database.delete_image(image_id)

        if not success:
            log_error(f'Failed to delete image file with id: {image_id}')
            return jsonify({'error': f'Failed to delete image file with id: {image_id}'}, 500)

        delete_file(filename)

        return jsonify({
            'success': True,
            'message': f'Image with id: {image_id} deleted succffessfuly)'
            }, 200)
