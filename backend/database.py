"""database.oy"""

# from datetime import datetime
from typing import List, Optional, Tuple
import psycopg2
from psycopg2.extras import DictCursor

from config import Config
from models import Image
from utils import log_debug, log_error, log_info, log_success


class Database():

    @staticmethod
    def get_connection():
        # TODO add connections pool
        log_debug(Config.DATABASE_URL)
        return psycopg2.connect(Config.DATABASE_URL)

    @staticmethod
    def init_db():
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS images(
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        original_name TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT NOT NULL
                    )
                ''')
                conn.commit()
                log_info('Database initialized')
        except Exception as e:
            log_error(f'Error init DB {e}')
        finally:
            if conn:
                conn.close()

    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO images(filename, original_name, size, file_type)
                    VALUES(%s, %s, %s, %s) RETURNING id
                ''', (image.filename, image.original_name, image.size, image.file_type))
                # image_id = 1
                id_data = cursor.fetchone()
                image_id = id_data[0] if id_data else None
                conn.commit()
                log_success(f'Image saved to DB: {image.filename}, ID: {image_id}')
                return True, image_id
        except Exception as e:
            log_error(f'Error image save to DB {e}')
            return False, None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_images(page: int = 0, per_page: int = Config.IMAGES_PER_PAGE) -> Tuple[List[Image], int]:
        """Get paged images from DB

        Args:
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to Config.IMAGES_PER_PAGE.

        Returns:
            Tuple[List[Image], int]: images array, total images (-1 when error occurred)
        """
        conn = None
        try:
            conn = Database.get_connection()
            offset = page * per_page
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute('''
                    SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s
                ''', (per_page, offset))
                rows = cursor.fetchall()
                images = [
                    Image(
                        id=row['id'],
                        filename=row['filename'],
                        original_name=row['original_name'],
                        size=row['size'],
                        upload_time=row['upload_time'],
                        file_type=row['file_type']
                    )
                    for row in rows
                ]
                cursor.execute('SELECT COUNT(*) AS total FROM IMAGES')
                # total = cursor.fetchone()[0]
                total_data = cursor.fetchone()
                total = total_data['total'] if total_data else 0
                return images, total
        except Exception as e:
            log_error(f'Error get images from DB {e}')
            return [], -1
        finally:
            if conn:
                conn.close()

    @staticmethod
    def delete_image(image_id: int) -> Tuple[bool, Optional[str]]:
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT filename FROM images WHERE id = %s
                ''', (image_id, ))
                row = cursor.fetchone()
                if not row:
                    return False, None

                filename = row[0]
                cursor.execute('''
                    DELETE FROM images WHERE id = %s
                ''', (image_id, ))
                conn.commit()
                log_success(f'Image with id: {image_id} deleted from DB: {filename}')
                return True, filename
        except Exception as e:
            log_error(f'Error image delete from DB {e}')
            return False, None
        finally:
            if conn:
                conn.close()
