from PyQt6.QtWidgets import QDialog, QWidget
from PyQt6.QtGui import QColor

class ThemeHelper:
    @staticmethod
    def apply_popup_theme(dialog: QDialog, is_dark: bool):
        """
        is_dark bayrağına dayalı olarak QDialog veya QWidget'a kapsamlı bir stil sayfası uygular.
        """
        if is_dark:
            bg_color = "#1F2937"  # Gray-900 (Arka Plan)
            text_color = "#F9FAFB" # Gray-50 (Metin)
            input_bg = "#374151"   # Gray-700 (Girdiler)
            border_color = "#4B5563" # Gray-600
            btn_primary = "#2563EB" # Blue-600
            btn_secondary = "#4B5563" # Gray-600
            
            style = f"""
                QDialog, QWidget {{ 
                    background-color: {bg_color}; 
                    color: {text_color}; 
                }}
                QLabel {{ color: {text_color}; }}
                QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
                    background-color: {input_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px; /* Artırılmış dolgu */
                }}
                /* Geliştirilmiş QComboBox Stili */
                QComboBox {{ 
                    padding: 6px; 
                    padding-right: 20px; 
                    font-size: 13px; 
                }}
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 0px;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                }}
                QComboBox::down-arrow {{
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNFNUU3RUIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNiA5bDYgNiA2LTYiLz48L3N2Zz4=);
                    width: 12px;
                    height: 12px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {input_bg};
                    color: {text_color};
                    selection-background-color: {btn_primary};
                    selection-color: white;
                    border: 1px solid {border_color};
                    outline: none;
                    min-width: 250px; /* Geniş açılır pencereyi zorla */
                }}
                QComboBox QAbstractItemView::item {{
                    min-height: 30px; /* Standart görünür öğeler */
                    padding: 4px;
                    font-size: 13px;
                }}

                /* Liste Görünümleri */
                QListView {{
                    background-color: {input_bg};
                    color: {text_color};
                    selection-background-color: {btn_primary};
                    selection-color: white;
                    border: 1px solid {border_color};
                }}
                QListWidget {{
                    background-color: {input_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                }}
                QListWidget::item:selected {{
                    background-color: {btn_primary};
                    color: white;
                }}

                QPushButton {{
                    background-color: {btn_primary};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #1D4ED8; }}
                
                QHeaderView::section {{
                    background-color: {input_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                }}
                QTableWidget {{
                    background-color: {input_bg};
                    color: {text_color};
                    gridline-color: {border_color};
                }}
            """
        else:
            # Açık Mod varsayılanları (Sistem veya Özel)
            bg_color = "#FFFFFF"
            text_color = "#111827"
            input_bg = "#FFFFFF"
            border_color = "#D1D5DB"
            btn_primary = "#3B82F6"
            
            style = f"""
                QDialog, QWidget {{ 
                    background-color: {bg_color}; 
                    color: {text_color}; 
                }}
                QLabel {{ color: {text_color}; }}
                QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
                    background-color: {input_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px; /* Artırılmış dolgu */
                }}
                
                /* Geliştirilmiş QComboBox Stili */
                QComboBox {{ 
                    padding: 6px; 
                    padding-right: 20px; 
                    font-size: 13px; 
                    border: 1px solid #D1D5DB; 
                    border-radius: 4px;
                }}
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 0px;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                }}
                QComboBox::down-arrow {{
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMzNzQxNTEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNiA5bDYgNiA2LTYiLz48L3N2Zz4=);
                    width: 12px;
                    height: 12px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {input_bg};
                    color: {text_color};
                    selection-background-color: {btn_primary};
                    selection-color: white;
                    border: 1px solid {border_color};
                    outline: none;
                    min-width: 250px; /* Geniş açılır pencereyi zorla */
                }}
                QComboBox QAbstractItemView::item {{
                    min-height: 30px; /* Standart görünür öğeler */
                    padding: 4px;
                    font-size: 13px;
                }}

                QPushButton {{
                    background-color: {btn_primary};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #2563EB; }}
            """
            
        dialog.setStyleSheet(style)

    @staticmethod
    def get_chart_colors(is_dark: bool):
        """
        Matplotlib grafikleri için bir renk sözlüğü döndürür.
        """
        if is_dark:
            return {
                'facecolor': '#1F2937', # Arka Plan
                'text': '#E5E7EB',      # Metin
                'edge': '#E5E7EB',
                'grid': '#374151',
                'bar': '#3B82F6',       # Mavi çubuklar
                'line': '#10B981'       # Yeşil çizgiler
            }
        else:
            return {
                'facecolor': '#FFFFFF',
                'text': '#111827',
                'edge': '#111827',
                'grid': '#E5E7EB',
                'bar': '#3B82F6',
                'line': '#10B981'
            }
