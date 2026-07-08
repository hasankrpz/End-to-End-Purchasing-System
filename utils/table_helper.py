from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtGui import QColor, QBrush
from utils.text_utils import turkish_lower

class TableHelper:
    @staticmethod
    def highlight_search_results(table: QTableWidget, search_text: str, is_dark: bool = False):
        """
        Tablodaki metni arar ve eşleşen hücreleri vurgular.
        Eşleşmeyen hücreler için arka planı sıfırlar.
        """
        if not search_text:
            # Vurguları temizle
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setBackground(QBrush()) 
                        item.setForeground(QBrush()) # Gerekirse metin rengini sıfırla
            return

        search_text = turkish_lower(search_text)
        
        # Vurgu Renklerini Tanımla
        if is_dark:
            # Karanlık Mod Vurgusu (örn. Sönük Kehribar/Turuncu)
            highlight_color = QColor("#92400E") # Amber-800
            text_color = QColor("#FEF3C7")      # Amber-100
        else:
            # Açık Mod Vurgusu (örn. Parlak Sarı)
            highlight_color = QColor("#FEF08A") # Yellow-200
            text_color = QColor("#000000")      # Black

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    txt = turkish_lower(item.text())
                    if search_text in txt:
                        item.setBackground(highlight_color)
                        item.setForeground(text_color)
                    else:
                        item.setBackground(QBrush()) 
                        item.setForeground(QBrush())

