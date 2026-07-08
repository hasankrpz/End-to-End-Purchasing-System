from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.filterable_table import FilterHeader
from utils.table_helper import TableHelper
from utils.text_utils import turkish_lower

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text().replace(".", "").replace(",", ".")) < float(other.text().replace(".", "").replace(",", "."))
        except ValueError:
            return super().__lt__(other)

class PageSATAcik(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logger = Logger()
        self.init_ui()

    def showEvent(self, event):
        """Sayfa görüntülendiğinde verileri yenile"""
        self.load_data()
        super().showEvent(event)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # ÜST ÇUBUK
        top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Açık Satın Alma Talepleri")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Açık Talep Ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)

        top_bar.addStretch()

        self.btn_approve = QPushButton("Onayla / Kapat")
        self.btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_approve.clicked.connect(self.approve_request)
        top_bar.addWidget(self.btn_approve)
        
        self.btn_reject = QPushButton("Reddet")
        self.btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reject.clicked.connect(self.reject_request)
        top_bar.addWidget(self.btn_reject)

        self.layout.addLayout(top_bar)

        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Talep Eden", "Ürün", "Miktar", "Durum", "Tarih"])
        
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
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E5E7EB;")
            self.search_input.setStyleSheet("padding: 8px; border: 1px solid #4B5563; border-radius: 6px; background-color: #1F2937; color: #F9FAFB;")
            self.btn_approve.setStyleSheet("""
                QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} 
                QPushButton:hover { background-color: #047857; }
            """)
            self.btn_reject.setStyleSheet("""
                QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} 
                QPushButton:hover { background-color: #7F1D1D; }
            """)
            
            self.btn_reset.setStyleSheet("""
                QPushButton { background-color: #374151; color: #E5E7EB; padding: 6px 12px; border-radius: 6px; border: 1px solid #4B5563; font-weight: bold;} 
                QPushButton:hover { background-color: #4B5563; }
            """)
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #111827; color: #E5E7EB; gridline-color: #374151; border: none; alternate-background-color: #1F2937; }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section { background-color: #1F2937; color: #9CA3AF; border: none; border-bottom: 2px solid #374151; padding: 4px; font-weight: bold; }
                QHeaderView::section:vertical { border-right: 1px solid #374151; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
            self.table.setAlternatingRowColors(True)
        else:
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827;")
            self.search_input.setStyleSheet("padding: 8px; border: 1px solid #D1D5DB; border-radius: 6px; background-color: #FFFFFF; color: #111827;")
            self.btn_approve.setStyleSheet("""
                QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #059669; }
            """)
            self.btn_reject.setStyleSheet("""
                QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #DC2626; }
            """)
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)

            self.btn_reset.setStyleSheet("""
                QPushButton { background-color: #6B7280; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #4B5563; }
            """)

    def reset_filters(self):
        """Filtreleri sıfırlar ve tabloyu yeniler"""
        self.search_input.clear()
        if hasattr(self, 'filter_header'):
            self.filter_header.clear_filters()
        self.load_data()

    def approve_request(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen onaylanacak bir talep seçin.")
            return

        req_id = self.table.item(row, 0).text()
        status_item = self.table.item(row, 4) # 4. sütun Durumdur
        current_status = status_item.text() if status_item else ""

        if current_status == "Onaylandı":
            CustomDialogs.info(self, "Bu talep zaten onaylanmış.")
            return
        
        if current_status != "Bekliyor":
            CustomDialogs.warning(self, f"Sadece 'Bekliyor' durumundaki talepler onaylanabilir. Mevcut durum: {current_status}")
            return

        if CustomDialogs.question(self, f"ID: {req_id} nolu talebi onaylamak istediğinize emin misiniz?", "Onay"):
            self.db.connect()
            try:
                # 'Onaylandı' için Durum Kimliğini Al
                st = self.db.cursor.execute("SELECT status_id FROM request_statuses WHERE status_name='Onaylandı'").fetchone()
                if st:
                    approved_status_id = st[0]
                    self.db.cursor.execute("UPDATE purchase_requests SET status_id=? WHERE request_id=?", (approved_status_id, req_id))
                    self.db.conn.commit()
                    self.logger.info(f"Talep onaylandı. ID: {req_id}")
                    CustomDialogs.info(self, "Talep onaylandı.")
                    self.load_data()
                else:
                    CustomDialogs.error(self, "'Onaylandı' durum tanımı bulunamadı!")
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, str(e))
                self.logger.error(f"Talep onaylama hatası: {e}")
            finally:
                self.db.disconnect()

    def reject_request(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen reddedilecek bir talep seçin.")
            return

        req_id = self.table.item(row, 0).text()
        status_item = self.table.item(row, 4)
        current_status = status_item.text() if status_item else ""

        if current_status != "Bekliyor":
            CustomDialogs.warning(self, f"Sadece 'Bekliyor' durumundaki talepler reddedilebilir. Mevcut durum: {current_status}")
            return

        if CustomDialogs.question(self, f"ID: {req_id} nolu talebi REDDETMEK istediğinize emin misiniz?", "Reddet"):
            self.db.connect()
            try:
                # 'Reddedildi' için Durum Kimliğini Al
                st = self.db.cursor.execute("SELECT status_id FROM request_statuses WHERE status_name='Reddedildi'").fetchone()
                if st:
                    rejected_status_id = st[0]
                    self.db.cursor.execute("UPDATE purchase_requests SET status_id=? WHERE request_id=?", (rejected_status_id, req_id))
                    self.db.conn.commit()
                    self.logger.info(f"Talep reddedildi. ID: {req_id}")
                    CustomDialogs.info(self, "Talep reddedildi.")
                    self.load_data()
                else:
                    CustomDialogs.error(self, "'Reddedildi' durum tanımı bulunamadı!")
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, str(e))
                self.logger.error(f"Talep reddetme hatası: {e}")
            finally:
                self.db.disconnect()

    def load_data(self):
        self.table.setSortingEnabled(False)
        search = self.search_input.text()
        search_lower = turkish_lower(search)

        query = """
            SELECT pr.request_id, u.first_name || ' ' || COALESCE(u.last_name, ''), i.item_name, pr.quantity, st.status_name, pr.created_at
            FROM purchase_requests pr
            LEFT JOIN users u ON pr.requester_user_id = u.user_id
            JOIN items i ON pr.item_id = i.item_id
            LEFT JOIN request_statuses st ON pr.status_id = st.status_id
            WHERE st.status_name = 'Bekliyor'
        """
        
        query += " ORDER BY pr.request_id ASC"

        self.db.connect()
        try:
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            # Python'da Sonuçları Filtrele
            filtered_rows = []
            if search:
                for row in rows:
                    # Tüm sütunları metne dönüştür (None hariç) ve kontrol et
                    row_text = " ".join([str(val) for val in row if val is not None])
                    if search_lower in turkish_lower(row_text):
                        filtered_rows.append(row)
            else:
                filtered_rows = rows
            
            self.table.setRowCount(0)
            self.table.setSortingEnabled(False) # Ekleme sırasında sıralamayı devre dışı bırak
            for r_idx, row in enumerate(filtered_rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    if c_idx == 3:
                        item = NumericTableWidgetItem(str(val))
                    else:
                        item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)
            
            # Arama sonuçlarını vurgula
            is_dark = getattr(self, 'is_dark', False)
            TableHelper.highlight_search_results(self.table, search, is_dark)
            
            # Varsa filtreleri tekrar uygula
            if hasattr(self.table.horizontalHeader(), 'apply_filters'):
                self.table.horizontalHeader().apply_filters()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.db.disconnect()
            self.table.setSortingEnabled(False)
