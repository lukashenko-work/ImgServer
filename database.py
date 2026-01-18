"""database.oy"""

import psycopg2

from config import Config


class Database():

    @staticmethod
    def get_connection():
        return psycopg2.connect(Config.DATABASE_URL)


    @staticmethod
    def init_db():
        conn = Database.get_connection()
        try:
            pass
        except:
            pass
