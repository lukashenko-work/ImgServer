"""Backup module"""


from datetime import datetime
from os import path
import subprocess
import sys
from config import Config
from utils import ensure_backups_dir, format_file_size, log_error, log_info, setup_logging


def create_backup():
    """Create backup"""
    try:
        db_url = Config.DATABASE_URL
        db_url = db_url.replace('postgresql://', '')

        parts = db_url.split('@')

        user_pass = parts[0]
        host_port_db = parts[1]

        user, password = user_pass.split('":')

        host_port, db_name = host_port_db.split('/')

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'

        timestamp = datetime.now().strftime(Config.BACKUP_TIMESTAMP_FORMAT)
        backup_filename = f'backup_{timestamp}.sql'
        backup_file_path = path.join(Config.BACKUP_FOLDER, backup_filename)

        # Команда для создания бэкапа
        pg_dump_cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', db_name,
            '-f', backup_file_path
        ]

        log_info(f'Creating backup to: {backup_filename}')

        result = subprocess.run(
            pg_dump_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            file_size = path.getsize(backup_file_path)
            size_formatted = format_file_size(file_size)
            log_info(f'Backup successfully created at {backup_filename} ({size_formatted})')

            return True, backup_filename
        else:
            log_error(f'Error: {result.stderr}')
            return False, result.stderr
    except Exception as e:
        log_error(f'Error: {e}')
        return False, str(e)


def restore_backup(backup_filename: str):
    """Restore backup"""
    try:
        db_url = Config.DATABASE_URL
        db_url = db_url.replace('postgresql://', '')

        parts = db_url.split('@')

        user_pass = parts[0]
        host_port_db = parts[1]

        user, password = user_pass.split('":')

        host_port, db_name = host_port_db.split('/')

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'

        backup_file_path = path.join(Config.BACKUP_FOLDER, backup_filename)

        # Команда для восстановления бэкапа
        pg_restore_cmd = [
            'pg_restore',
            '-C',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', db_name,
            backup_file_path
        ]

        log_info(f'Restoring backup from: {backup_filename}')

        result = subprocess.run(
            pg_restore_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            log_info(f'Backup successfully restored from {backup_filename}')

            return True, backup_filename
        else:
            log_error(f'Error: {result.stderr}')
            return False, result.stderr
    except Exception as e:
        log_error(f'Error: {e}')
        return False, str(e)


if __name__ == '__main__':
    setup_logging()
    ensure_backups_dir()

    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) > 2:
            backup_file = sys.argv[2]
            success, result = restore_backup(backup_file)
            if success:
                print(f'Backup {result} successfully restored. See logs.')
            else:
                print(f'Error restoring from backup: {result}.  See logs.')
        else:
            print('Specify file to restore')
    else:
        success, result = create_backup()
        if success:
            print(f'Backup successfully created ({result}). See logs.')
        else:
            print(f'Error creating backup: {result}. See logs.')
