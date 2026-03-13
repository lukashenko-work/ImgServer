"""database.oy"""

from contextlib import contextmanager
import logging
import sys
from typing import List, Optional, Tuple
from psycopg2 import pool
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import NamedTupleCursor

from config import Config
from models import Image
from utils import log_critical, log_debug, log_error, log_info, log_success

# connection_pool: ThreadedConnectionPool

# try:
#     conn_pool = pool.ThreadedConnectionPool(1, 20, Config.DATABASE_URL)
# except (Exception) as e:
#     print('Ошибка при подключении к БД', e)

# TODO: do Database a singleton. Move connection pool inside the class
# try:
#     conn_pool = pool.ThreadedConnectionPool(1, 20, Config.DATABASE_URL, cursor_factory=NamedTupleCursor)
# except Exception as e:
#     print('Error getting connection pool', e)

logger = logging.getLogger(__name__)


def do_something():
    logger.debug("Это отладочное сообщение")
    logger.info("Модуль выполняет действие")
    try:
        t = 1 / 0
        print(t)
    except ZeroDivisionError:
        logger.exception("Произошла ошибка деления на ноль")


do_something()


class Database():

    __connection_pool: ThreadedConnectionPool
    __str: str

    # @staticmethod
    # def get_connection():
    #     log_debug(Config.DATABASE_URL)
    #     return psycopg2.connect(Config.DATABASE_URL, cursor_factory=NamedTupleCursor)

    @staticmethod
    @contextmanager
    def get_connection():
        """Use get_connection for manual transaction control and change the cursor factory

        Yields:
            connection: DB connection
        """
        conn = Database.__connection_pool.getconn()
        try:
            with conn:
                yield conn
        finally:
            Database.__connection_pool.putconn(conn)

    @staticmethod
    @contextmanager
    def get_cursor():
        """with connection and cursor automatically commit assume

        Yields:
            cursor: DB cursor
        """
        conn = Database.__connection_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    yield cursor
            # yield connection.cursor(cursor_factory=NamedTupleCursor). Now cursor factory specified in connection
        except Exception as e:
            log_error(f'1 Unable to get cursor from connection pool {e}')
            logger.error(f'2 Unable to get cursor from connection pool {e}')
            logger.exception(e)
        finally:
            Database.__connection_pool.putconn(conn)

    @staticmethod
    def init_db():
        Database.create_connection_pool()

        try:
            with Database.get_cursor() as cursor:
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
                log_info('1 Database initialized')
                logger.info('2 Database initialized')
        except Exception as e:
            log_error(f'1 Error init DB {e}')
            logger.error(f'2 Error init DB {e}')
            logger.exception(e)

    @staticmethod
    def create_connection_pool():
        """Creates ThreadedConnectionPool
        """
        try:
            log_debug('1 ' + Config.DATABASE_URL)
            logger.debug('2 ' + Config.DATABASE_URL)
            Database.__connection_pool = pool.ThreadedConnectionPool(1, 20, Config.DATABASE_URL, cursor_factory=NamedTupleCursor)
            log_info('1 Connection pool initialized')
            logger.info('2 Connection pool initialized')
        except Exception as e:
            log_critical('1 FATAL ERROR: Unable to initialize connection pool. Application terminated.')
            logger.critical('2 FATAL ERROR: Unable to initialize connection pool. Application terminated.')
            # log_exception(e)
            logger.exception(e)
            sys.exit(1)

    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        try:
            with Database.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO images(filename, original_name, size, file_type)
                    VALUES(%s, %s, %s, %s) RETURNING id
                ''', (image.filename, image.original_name, image.size, image.file_type))
                id_data = cursor.fetchone()
                # image_id = id_data[0] if id_data else None
                image_id = id_data.id if id_data else None
                log_success(f'1 Image saved to DB: {image.filename}, ID: {image_id}')
                logger.info(f'2 Image saved to DB: {image.filename}, ID: {image_id}')
                return True, image_id
        except Exception as e:
            log_error(f'1 Error image save to DB {e}')
            logger.error(f'2 Error image save to DB {e}')
            logger.exception(e)
            return False, None

    @staticmethod
    def get_images(page: int = 0, per_page: int = Config.IMAGES_PER_PAGE, random: bool = False) -> Tuple[List[Image], int, int]:
        """Get paged images from DB, common function

        Args:
            page (int, optional): Page for pagination. Defaults to 1.
            per_page (int, optional): Images per page. Defaults to Config.IMAGES_PER_PAGE.
            random (bool, optional): If True, return random images, otherwise sorting by upload_time DESC. Defaults to False.

        Returns:
            Tuple[List[Image], int, int]: images array, total images (-1 when error occurred), current page
        """
        try:
            if page < 0:
                page = 0
            offset = page * per_page
            with Database.get_cursor() as cursor:
                cursor.execute('SELECT COUNT(*) AS total FROM IMAGES')
                # total = cursor.fetchone()[0]
                total_data = cursor.fetchone()
                # total = total_data['total'] if total_data else 0
                total = total_data.total
                if total > 0 and total <= offset:  # Requested non-existent page (more then exists)
                    # calculating last page
                    mod = total % per_page
                    pages = total // per_page
                    if mod == 0:
                        page = pages - 1
                    else:
                        page = pages
                    offset = page * per_page
                if random:
                    cursor.execute('''
                        SELECT * FROM images ORDER BY RANDOM() LIMIT %s
                    ''', (per_page, ))
                else:
                    cursor.execute('''
                    SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s
                    ''', (per_page, offset))
                rows = cursor.fetchall()
                # images = [
                #     Image(
                #         id=row['id'],
                #         filename=row['filename'],
                #         original_name=row['original_name'],
                #         size=row['size'],
                #         upload_time=row['upload_time'],
                #         file_type=row['file_type']
                #     )
                #     for row in rows
                # ]
                images = [
                    Image(
                        id=row.id,
                        filename=row.filename,
                        original_name=row.original_name,
                        size=row.size,
                        upload_time=row.upload_time,
                        file_type=row.file_type
                    )
                    for row in rows
                ]
                return images, total, page
        except Exception as e:
            log_error(f'1 Error get images from DB {e}')
            logger.error(f'2 Error get images from DB {e}')
            logger.exception(e)
            return [], -1, 0

    @staticmethod
    def get_paged_images(page: int = 0, per_page: int = Config.IMAGES_PER_PAGE) -> Tuple[List[Image], int, int]:
        """Get paged images from DB

        Args:
            page (int, optional): Page for pagination. Defaults to 1.
            per_page (int, optional): Images per page. Defaults to Config.IMAGES_PER_PAGE.

        Returns:
            Tuple[List[Image], int, int]: images array, total images (-1 when error occurred), current page
        """
        return Database.get_images(page, per_page, random=False)

    @staticmethod
    def get_random_images() -> Tuple[List[Image], int, int]:
        """Gets random per page images

        Returns:
            Tuple[List[Image], int, int]: Random images array, total images (-1 when error occurred), current page
        """
        return Database.get_images(random=True)

    @staticmethod
    def delete_image(image_id: int) -> Tuple[bool, Optional[str]]:
        """Delete image from DB by ID

        Args:
            image_id (int): Image ID

        Returns:
            Tuple[bool, Optional[str]]: success, message
        """
        try:
            with Database.get_cursor() as cursor:
                cursor.execute('''
                    SELECT filename FROM images WHERE id = %s
                ''', (image_id, ))
                row = cursor.fetchone()
                if not row:
                    return False, None

                filename = row.filename
                cursor.execute('''
                    DELETE FROM images WHERE id = %s
                ''', (image_id, ))
                log_success(f'1 Image with id: {image_id} deleted from DB: {filename}')
                logger.info(f'2 Image with id: {image_id} deleted from DB: {filename}')
                return True, filename
        except Exception as e:
            log_error(f'1 Error image delete from DB {e}')
            logger.error(f'2 Error image delete from DB {e}')
            logger.exception(e)
            return False, None
