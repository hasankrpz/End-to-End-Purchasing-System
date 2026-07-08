import sys
import os

# FAKETIME entegrasyonu: Uygulamayı 2025 yılında çalışmaya zorla
# Eğer FAKETIME ortam değişkeni yoksa, kendini faketime ile yeniden başlat
if "FAKETIME" not in os.environ and "SCARF_NO_ANALYTICS" not in os.environ: # SCARF check prevents loop if env vars leak
    target_date = "2025-12-25"
    faketime_path = "/opt/homebrew/bin/faketime"
    
    if os.path.exists(faketime_path):
        os.environ["FAKETIME"] = target_date
        # Mevcut Python interpreter ve argümanlarla yeniden başlat
        args = [faketime_path, target_date, sys.executable] + sys.argv
        print(f"Uygulama faketime ({target_date}) ile yeniden başlatılıyor...")
        os.execv(faketime_path, args)
    else:
        print("UYARI: faketime bulunamadı (/opt/homebrew/bin/faketime). Normal sistem saatiyle devam ediliyor.")
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from forms.frm_main import MainWindow
from database.db_manager import DatabaseManager
from utils.logger import Logger
import os
import PyQt6
try:
    import resources_rc
except ImportError as e:
    logger = Logger()
    logger.error(f"Resource import failed: {e}")

dirname = os.path.dirname(PyQt6.__file__)
# plugin_path removed as it caused issues with correct path resolution in newer/split PyQt6 installs

def create_padded_icon(icon_path_or_pm, padding_ratio=0.2):
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import Qt, QSize
    
    if isinstance(icon_path_or_pm, QPixmap):
        orig_pixmap = icon_path_or_pm
    else:
        orig_pixmap = QPixmap(icon_path_or_pm)

    if orig_pixmap.isNull():
        return QIcon()

    size = orig_pixmap.size()
    max_dim = max(size.width(), size.height())
    
    new_size = int(max_dim / (1 - padding_ratio))
    final_pixmap = QPixmap(new_size, new_size)
    final_pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(final_pixmap)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    
    x = (new_size - size.width()) // 2
    y = (new_size - size.height()) // 2
    
    painter.drawPixmap(x, y, orig_pixmap)
    painter.end()
    
    return QIcon(final_pixmap)

def main():
    logger = Logger()
    logger.info("Uygulama başlatılıyor...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("HAB Purchasing")
    app.setApplicationDisplayName("HAB Purchasing")
    app.setOrganizationName("HAB Systems")
    app.setOrganizationDomain("habsystems.com")
    app.setApplicationVersion("1.0.0")
    
    try:
        db = DatabaseManager()
        if db.connect():
            logger.info("Veritabanı bağlantısı başarılı.")
            db.initialize_database()
            db.disconnect()
        else:
            logger.error("Veritabanına bağlanılamadı.")

        window = MainWindow()
        app_icon = QIcon(":/resources/icon.png") 
        
        window.setWindowIcon(app_icon)
        app.setWindowIcon(app_icon) 

        # Pencereyi göster ve öne getir
        window.show()
        window.raise_()
        window.activateWindow()
        
        exit_code = app.exec() 
        logger.info(f"Uygulama kapatılıyor. Çıkış kodu: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Kritik Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()