import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.setup()
        return cls._instance

    def setup(self):
        import sys
        
        if getattr(sys, 'frozen', False):
            # PROD: .exe olarak çalışıyor
            # Kullanıcının Belgelerim klasörüne kaydedelim ki kolay bulsun
            documents_path = os.path.expanduser("~/Documents")
            self.log_dir = os.path.join(documents_path, "YBS_Logs")
        else:
            # DEV: Geliştirme ortamı
            # Proje klasörü içindeki logs klasörü
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_dir = os.path.join(base_dir, "logs")
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = logging.getLogger("YBS_Logger")
        self.logger.setLevel(logging.DEBUG)

        # Dosya İşleyicisi - Günlük Döndür
        log_file = os.path.join(self.log_dir, "application.log")
        file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8')
        file_handler.suffix = "%Y-%m-%d"
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Konsol İşleyicisi
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)
