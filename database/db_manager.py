import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="purchasing.db"):
        import sys
        import shutil
        
        self.conn = None
        self.cursor = None

        if getattr(sys, 'frozen', False):
            # Derlenmiş paket içinde çalışıyor
            base_path = sys._MEIPASS
            exe_dir = os.path.dirname(sys.executable)
            
            # Kalıcı veritabanı .exe dosyasının yanında olmalı
            persistent_db_path = os.path.join(exe_dir, db_name)
            
            # Paketlenmiş veritabanı (kaynak)
            bundled_db_path = os.path.join(base_path, db_name)

            if not os.path.exists(persistent_db_path):
                try:
                    # Paketten kalıcı konuma kopyala
                    shutil.copy2(bundled_db_path, persistent_db_path)
                    print(f"Veritabanı kopyalandı: {persistent_db_path}")
                except Exception as e:
                    print(f"Veritabanı kopyalama hatası: {e}")
            
            self.db_name = persistent_db_path
        else:
            # Normal Python ortamında çalışıyor

            self.db_name = db_name

    def connect(self):
        try:
            # Get the absolute path to the database file
            # Assuming db_manager.py is in database/ folder, and purchasing.db is in root or we use a fixed path
            # The app seems to use "purchasing.db" in the current working directory (root) based on main.py execution context.
            
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute("PRAGMA foreign_keys = ON") #Foreign Key desteğini aç desteğini açar
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def initialize_database(self):
        # tables.sql dosyasını okur ve tabloları yoksa oluşturur.
        try:
            # Bu dosyaya göre tables.sql yolunu bul

            current_dir = os.path.dirname(os.path.abspath(__file__))
            sql_file_path = os.path.join(current_dir, "tables.sql")
            
            if not os.path.exists(sql_file_path):
                print(f"Error: tables.sql not found at {sql_file_path}")
                return False

            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_script = f.read()

            if self.conn:
                self.conn.executescript(sql_script)
                self.conn.commit()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            if self.conn:
                self.conn.rollback()
            return False
