from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QPushButton, QGraphicsDropShadowEffect, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

class NotificationPopup(QFrame):
    def __init__(self, parent=None):
        # Parent=None, üst düzey bağımsız pencere mantığı olduğundan emin olmak için
        # Ancak yaşam döngüsünü dikkatlice yöneteceğiz.
        super().__init__(parent) 
        
        # Bu artık bir "Pencere" değil, sadece bir widget (Katman)
        # üst öğe üzerinden konumlandırılacak.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setFixedSize(320, 350)
        self.hide() # Başlangıçta gizle
        
        # 1. Ana Düzen (Kök)
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(5, 5, 5, 5) 
        self.root_layout.setSpacing(0)

        # 2. İç Konteyner 
        self.container = QFrame()
        self.container.setObjectName("PopupContainer")
        self.container.setStyleSheet("""
            QFrame#PopupContainer {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 8px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f2f6;
                color: #34495e;
            }
            QListWidget::item:hover {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: transparent;
                color: #e74c3c;
                border: none;
                font-weight: bold;
                text-align: right;
                padding-right: 15px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        # Gölge Efekti
        shadow = QGraphicsDropShadowEffect(self.container)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.container.setGraphicsEffect(shadow)
        
        self.root_layout.addWidget(self.container)

        # 3. İçerik Düzeni
        self.content_layout = QVBoxLayout(self.container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # 3a. Başlık
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(45)
        self.header_frame.setStyleSheet("background-color: #ffffff; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom: 1px solid #f1f2f6;")
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_title = QLabel("Bildirimler")
        lbl_title.setStyleSheet("font-size: 15px; border: none;")
        header_layout.addWidget(lbl_title)
        
        self.content_layout.addWidget(self.header_frame)

        # 3b. Liste
        self.list_widget = QListWidget()
        self.list_widget.addItems([
            "4 adet açık talep var.",
            "Sistem bakımı planlandı.",
            "Her şey yolunda. 🙂"
        ])
        self.content_layout.addWidget(self.list_widget)

        # 3c. Alt Kısım
        self.footer_frame = QFrame()
        self.footer_frame.setFixedHeight(40)
        self.footer_frame.setStyleSheet("background-color: #ffffff; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; border-top: none;")
        footer_layout = QVBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(0, 0, 10, 0)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.list_widget.clear)
        
        footer_layout.addWidget(self.btn_clear)
        self.content_layout.addWidget(self.footer_frame)

    def update_theme(self, is_dark):
        if is_dark:
            # Koyu Tema Renkleri
            bg_color = "#2c3e50"
            border_color = "#34495e"
            text_color = "#ecf0f1"
            header_bg = "#34495e"
            list_hover = "#3e5871"
            btn_text = "#e74c3c"
        else:
            # Açık Tema Renkleri (Varsayılan)
            bg_color = "#ffffff"
            border_color = "#dcdde1"
            text_color = "#2c3e50"
            header_bg = "#ffffff"
            list_hover = "#f5f6fa"
            btn_text = "#e74c3c"

        self.container.setStyleSheet(f"""
            QFrame#PopupContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                font-weight: bold;
                background-color: transparent;
                border: none;
            }}
            QListWidget {{
                border: none;
                background-color: transparent;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {border_color};
                color: {text_color};
            }}
            QListWidget::item:hover {{
                background-color: {list_hover};
            }}
            QPushButton {{
                background-color: transparent;
                color: {btn_text};
                border: none;
                font-weight: bold;
                text-align: right;
                padding-right: 15px;
            }}
            QPushButton:hover {{
                text-decoration: underline;
                color: {btn_text};
            }}
        """)
        
        # Başlık Özellikleri
        if hasattr(self, 'header_frame'):
             self.header_frame.setStyleSheet(f"background-color: {header_bg}; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom: 1px solid {border_color};")
        
        # Alt Kısım Özellikleri
        if hasattr(self, 'footer_frame'):
            self.footer_frame.setStyleSheet(f"background-color: {bg_color}; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; border-top: none;")
