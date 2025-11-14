import sqlite3
from datetime import datetime


class SettingsDB:
    def __init__(self, db_path='settings.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                input_file TEXT NOT NULL,
                output_file TEXT,
                operation_type TEXT NOT NULL,
                format TEXT NOT NULL,
                quality INTEGER,
                status TEXT NOT NULL,
                message TEXT,
                file_size_before INTEGER,
                file_size_after INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def set_value(self, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        conn.commit()
        conn.close()

    def get_value(self, key, default=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return default

    def get_bool(self, key, default=False):
        value = self.get_value(key, default)
        if isinstance(value, bool):
            return value
        if value in ('True', 'true', '1'):
            return True
        return False

    def get_int(self, key, default=0):
        value = self.get_value(key, default)
        try:
            return int(value)
        except:
            return default

    def clear(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM settings')
        conn.commit()
        conn.close()

    def add_conversion_record(self, input_file, output_file, operation_type,
                              format, quality, status, message, file_size_before=None, file_size_after=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO conversion_history 
            (timestamp, input_file, output_file, operation_type, format, quality, status, message, file_size_before, file_size_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            input_file,
            output_file,
            operation_type,
            format,
            quality,
            status,
            message,
            file_size_before,
            file_size_after
        ))

        conn.commit()
        conn.close()

    def get_conversion_history(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM conversion_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        columns = ['id', 'timestamp', 'input_file', 'output_file', 'operation_type',
                   'format', 'quality', 'status', 'message', 'file_size_before', 'file_size_after']

        return [dict(zip(columns, row)) for row in results]

    def clear_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversion_history')
        conn.commit()
        conn.close()

    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM conversion_history')
        total = cursor.fetchone()[0]

        cursor.execute(
            'SELECT COUNT(*) FROM conversion_history WHERE status = "success"')
        success = cursor.fetchone()[0]

        cursor.execute(
            'SELECT COUNT(*) FROM conversion_history WHERE status = "error"')
        error = cursor.fetchone()[0]

        cursor.execute('''
            SELECT operation_type, COUNT(*) 
            FROM conversion_history 
            GROUP BY operation_type
        ''')
        by_operation = dict(cursor.fetchall())

        cursor.execute('''
            SELECT format, COUNT(*) 
            FROM conversion_history 
            GROUP BY format
        ''')
        by_format = dict(cursor.fetchall())

        conn.close()

        return {
            'total': total,
            'success': success,
            'error': error,
            'success_rate': (success / total * 100) if total > 0 else 0,
            'by_operation': by_operation,
            'by_format': by_format
        }
