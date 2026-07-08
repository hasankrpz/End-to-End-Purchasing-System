from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QMessageBox, QAbstractItemView)

from utils.table_helper import TableHelper
from utils.text_utils import turkish_lower
from PyQt6.QtCore import Qt
import sqlite3
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.filterable_table import FilterHeader

# Sayısal sıralama için özelleştirilmiş öğe (Standarttan kopyalandı)
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text().replace(".", "").replace(",", ".")) < float(other.text().replace(".", "").replace(",", "."))
        except ValueError:
            return super().__lt__(other)

class PageSASAcik(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logger = Logger()
        self.init_ui()

    def showEvent(self, event):
        """Sayfa her görüntülendiğinde verileri yenile"""
        self.load_data()
        super().showEvent(event)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # 1. ÜST ÇUBUK
        top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Açık Siparişler")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Açık Sipariş Ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)

        top_bar.addStretch()

        # Teslim Al Düğmesi
        self.btn_receive = QPushButton("Teslim Al")
        self.btn_receive.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_receive.clicked.connect(self.mark_as_received)
        top_bar.addWidget(self.btn_receive)
        
        self.btn_cancel = QPushButton("İptal Et")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.cancel_order)
        top_bar.addWidget(self.btn_cancel)

        self.layout.addLayout(top_bar)

        # 2. TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Ürün", "Tedarikçi", "Miktar", "Fiyat", "Toplam", "T. Tarihi", "Durum"])
        
        # Özel Filtre Başlığını Ayarla
        self.filter_header = FilterHeader(self.table)
        self.table.setHorizontalHeader(self.filter_header)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False) 
        
        self.layout.addWidget(self.table)
        
        self.load_data()

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            # --- DARK MODE ---
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E5E7EB;")
            self.search_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px; 
                    border: 1px solid #4B5563; 
                    border-radius: 6px; 
                    background-color: #1F2937; 
                    color: #F9FAFB;
                }
                QLineEdit:focus { border: 1px solid #10B981; }
            """)
            
            # Düğme (Teslim Al - Mavi Tema)
            self.btn_receive.setStyleSheet("""
                QPushButton { background-color: #1E40AF; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; border: 1px solid #374151; }
                QPushButton:hover { background-color: #1E3A8A; }
            """)
            
            self.btn_cancel.setStyleSheet("""
                QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} 
                QPushButton:hover { background-color: #7F1D1D; }
            """)
            
            self.btn_reset.setStyleSheet("""
                QPushButton { background-color: #374151; color: #E5E7EB; padding: 6px 12px; border-radius: 6px; border: 1px solid #4B5563; font-weight: bold;} 
                QPushButton:hover { background-color: #4B5563; }
            """)
            
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #111827;
                    color: #E5E7EB;
                    gridline-color: #374151;
                    border: none;
                    alternate-background-color: #1F2937;
                }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section {
                    background-color: #1F2937;
                    color: #9CA3AF;
                    border: none;
                    border-bottom: 2px solid #374151;
                    padding: 4px;
                    font-weight: bold;
                }
                QHeaderView::section:vertical { border-right: 1px solid #374151; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
            self.table.setAlternatingRowColors(True)

        else:
            # --- LIGHT MODE ---
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827;")
            self.search_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px; 
                    border: 1px solid #D1D5DB; 
                    border-radius: 6px; 
                    background-color: #FFFFFF; 
                    color: #111827;
                }
                QLineEdit:focus { border: 1px solid #10B981; }
            """)
            
            self.btn_receive.setStyleSheet("""
                QPushButton { background-color: #3B82F6; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; border: none; }
                QPushButton:hover { background-color: #2563EB; }
            """)
            
            self.btn_cancel.setStyleSheet("""
                QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #DC2626; }
            """)

            self.btn_reset.setStyleSheet("""
                QPushButton { background-color: #6B7280; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #4B5563; }
            """)
            
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #1F2937;
                    gridline-color: #E5E7EB;
                    border: 1px solid #E5E7EB;
                    alternate-background-color: #F9FAFB;
                }
                QHeaderView::section {
                    background-color: #F3F4F6;
                    color: #4B5563;
                    border: none;
                    border-bottom: 1px solid #E5E7EB;
                    padding: 8px;
                    font-weight: bold;
                }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)



    def reset_filters(self):
        """Filtreleri sıfırlar ve tabloyu yeniler"""
        self.search_input.clear()
        if hasattr(self, 'filter_header'):
            self.filter_header.clear_filters()
        self.load_data()

    def load_data(self):
        """Veritabanından açık siparişleri çeker."""
        self.table.setSortingEnabled(False)
        search_text = self.search_input.text()
        search_lower = turkish_lower(search_text)

        # İptal veya Teslim Alınanlar HARİÇ
        query = """
            SELECT 
                po.order_id, 
                i.item_name, 
                s.company_name, 
                pr.quantity, 
                o.price, 
                (pr.quantity * o.price) as total_price,
                po.delivery_date, 
                st.status_name
            FROM purchase_orders po
            JOIN offers o ON po.offer_id = o.offer_id
            JOIN purchase_requests pr ON o.request_id = pr.request_id
            JOIN items i ON pr.item_id = i.item_id
            JOIN suppliers s ON o.supplier_id = s.supplier_id
            LEFT JOIN order_statuses st ON po.status_id = st.status_id
            WHERE st.status_name NOT IN ('Teslim Alındı', 'İptal')
        """
        
        query += " ORDER BY po.order_id DESC"

        self.db.connect()
        try:
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            # Python Filtresi
            filtered_rows = []
            if search_text:
                for row in rows:
                    # Arama için tüm satır verilerinin dize temsillerini birleştir
                    row_text = " ".join([str(val) for val in row if val is not None])
                    if search_lower in turkish_lower(row_text):
                        filtered_rows.append(row)
            else:
                filtered_rows = rows
            
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(filtered_rows):
                self.table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    val = data if data is not None else ""
                    
                    if col_idx in [0, 3, 4, 5]: # Sayısal
                        display_text = str(val)
                        if col_idx in [4, 5]: # Para
                             display_text = f"{val:,.2f}"
                        item = NumericTableWidgetItem(display_text)
                    else:
                        item = QTableWidgetItem(str(val))
                    
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)
            
            # Vurgula
            is_dark = getattr(self, 'is_dark', False)
            TableHelper.highlight_search_results(self.table, search_text, is_dark)

            # Varsa filtreleri tekrar uygula
            if hasattr(self.table.horizontalHeader(), 'apply_filters'):
                self.table.horizontalHeader().apply_filters()

        except Exception as e:
            print(f"Hata: {e}")
        finally:
            self.db.disconnect()
            self.table.setSortingEnabled(False)

    def mark_as_received(self):
        selected_row = self.table.currentRow()
        if selected_row < 0: # Seçimi kontrol etmek için orijinal mantık
            CustomDialogs.warning(self, "Lütfen teslim alınan siparişi seçin.")
            return

        order_id = self.table.item(selected_row, 0).text()
        
        if CustomDialogs.question(self, f"ID: {order_id} nolu siparişi fiziksel olarak eksiksiz teslim almak istediğinize emin misiniz?", "Teslimat Onayı"):
            self.db.connect()
            try:
                # 'Teslim Alındı' için Durum Kimliği
                delivered_status = self.db.cursor.execute("SELECT status_id FROM order_statuses WHERE status_name='Teslim Alındı'").fetchone()
                if delivered_status:
                    self.db.cursor.execute("UPDATE purchase_orders SET status_id=? WHERE order_id=?", (delivered_status[0], order_id))
                    self.logger.info(f"Sipariş teslim alındı olarak işaretlendi. ID: {order_id}")
                else:
                    CustomDialogs.error(self, "'Teslim Alındı' durumu bulunamadı.")
                
                self.db.conn.commit()
                CustomDialogs.info(self, "Seçili siparişler teslim alındı olarak işaretlendi.")
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, str(e))
                self.logger.error(f"Teslim alma işlemi hatası: {e}")
            finally:
                self.db.disconnect()

    def cancel_order(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            CustomDialogs.warning(self, "Lütfen iptal edilecek siparişi seçin.")
            return

        order_id = self.table.item(selected_row, 0).text()
        
        if CustomDialogs.question(self, f"ID: {order_id} nolu siparişi İPTAL ETMEK istediğinize emin misiniz?", "Siparişi İptal Et"):
            self.db.connect()
            try:
                # FK'lar dinamik olduğu için isim kullanarak Durum Kimliği
                st_cancel = self.db.cursor.execute("SELECT status_id FROM order_statuses WHERE status_name='İptal'").fetchone()
                if st_cancel:
                     self.db.cursor.execute("UPDATE purchase_orders SET status_id=? WHERE order_id=?", (st_cancel[0], order_id))
                     self.logger.info(f"Sipariş iptal edildi. ID: {order_id}")
                     self.db.conn.commit()
                     CustomDialogs.info(self, "Sipariş iptal edildi.")
                     self.load_data()
                else:
                     CustomDialogs.error(self, "'İptal' durum tanımı bulunamadı.")
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, str(e))
                self.logger.error(f"Sipariş iptal hatası: {e}")
            finally:
                self.db.disconnect()
