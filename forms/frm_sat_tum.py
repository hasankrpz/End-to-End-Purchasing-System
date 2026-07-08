from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QDialog, 
                             QFormLayout, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper
from utils.filterable_table import FilterHeader
from utils.table_helper import TableHelper
from utils.text_utils import turkish_lower

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text().replace(".", "").replace(",", ".")) < float(other.text().replace(".", "").replace(",", "."))
        except ValueError:
            return super().__lt__(other)

class PageSATTum(QWidget):
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
        self.lbl_title = QLabel("Tüm Satın Alma Talepleri")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Talep Ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)

        top_bar.addStretch()

        self.btn_change_status = QPushButton("Durum Değiştir")
        self.btn_change_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_change_status.clicked.connect(self.change_status)
        top_bar.addWidget(self.btn_change_status)

        self.layout.addLayout(top_bar)

        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Talep Eden", "Departman", "Ürün", "Miktar", "Durum", "Tarih"])
        
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
            
            self.btn_change_status.setStyleSheet("""
                QPushButton { background-color: #1E40AF; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #374151; font-weight: bold;} 
                QPushButton:hover { background-color: #1E3A8A; }
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
            
            self.btn_change_status.setStyleSheet("""
                QPushButton { background-color: #3B82F6; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #2563EB; }
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

    def load_data(self):
        self.table.setSortingEnabled(False)
        search = self.search_input.text()
        search_lower = turkish_lower(search)
        
        query = """
            SELECT pr.request_id, u.first_name || ' ' || COALESCE(u.last_name, ''), d.department_name, i.item_name, pr.quantity, st.status_name, pr.created_at
            FROM purchase_requests pr
            LEFT JOIN users u ON pr.requester_user_id = u.user_id
            LEFT JOIN departments d ON u.department_id = d.department_id
            JOIN items i ON pr.item_id = i.item_id
            LEFT JOIN request_statuses st ON pr.status_id = st.status_id
            WHERE 1=1
        """
        # SQL araması yok - Hepsini getir ve Python'da filtrele
        query += " ORDER BY pr.request_id DESC"

        self.db.connect()
        try:
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            # Sonuçları Python'da filtrele
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
                    if c_idx == 0 or c_idx == 4: # ID(0) ve Miktar(4) -> Sayısal Sıralama
                        item = NumericTableWidgetItem(str(val))
                    else:
                        item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)
            
            # Vurgula
            is_dark = getattr(self, 'is_dark', False)
            TableHelper.highlight_search_results(self.table, search, is_dark)

            # Filtreleri tekrar uygula
            if hasattr(self.table.horizontalHeader(), 'apply_filters'):
                self.table.horizontalHeader().apply_filters()
            
        except Exception as e:
            print(f"Error loading requests: {e}")
        finally:
            self.db.disconnect()
            self.table.setSortingEnabled(False)

    def change_status(self):
        """Seçili talebin durumunu değiştirir"""
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen durumu değiştirilecek bir talep seçin.")
            return

        req_id = self.table.item(row, 0).text()
        current_status = self.table.item(row, 5).text() # 5. sütun Durumdur

        # Mevcut durumları al
        try:
            self.db.connect()
            self.db.cursor.execute("SELECT status_name FROM request_statuses")
            statuses = [s[0] for s in self.db.cursor.fetchall()]
        except Exception as e:
            CustomDialogs.error(self, f"Durum listesi alınamadı: {e}")
            return
        finally:
            self.db.disconnect()
        
        # Yerelleştirme için Özel Diyalog
        dialog = QDialog(self)
        
        # Temayı Uygula
        is_dark = getattr(self, 'is_dark', False)
        ThemeHelper.apply_popup_theme(dialog, is_dark)
        
        dialog.setWindowTitle("Durum Değiştir")
        dialog.setFixedSize(300, 150)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Yeni Durum Seçin:"))
        
        combo_status = QComboBox()
        combo_status.addItems(statuses)
        combo_status.setCurrentText(current_status)
        layout.addWidget(combo_status)
        
        # Düğmeler
        from PyQt6.QtWidgets import QDialogButtonBox
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Tamam")
        btn_box.button(QDialogButtonBox.StandardButton.Cancel).setText("İptal")
        
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec():
            new_status = combo_status.currentText()
            if new_status and new_status != current_status:
                self.db.connect()
                try:
                    st = self.db.cursor.execute("SELECT status_id FROM request_statuses WHERE status_name=?", (new_status,)).fetchone()
                    if st:
                        self.db.cursor.execute("UPDATE purchase_requests SET status_id=? WHERE request_id=?", (st[0], req_id))
                        self.db.conn.commit()
                        self.logger.info(f"Talep durumu değiştirildi. Talep ID: {req_id}, Yeni Durum: {new_status}")
                        CustomDialogs.info(self, "Durum güncellendi.")
                        self.load_data()
                except Exception as e:
                    self.db.conn.rollback()
                    CustomDialogs.error(self, str(e))
                    self.logger.error(f"Durum değiştirme hatası: {e}")
                finally:
                    self.db.disconnect()

class RequestPopup(QDialog):
    """Yeni Talep Oluşturma Penceresi"""
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        self.setWindowTitle("Yeni Talep Oluştur")
        self.setFixedSize(350, 250)
        self.db = DatabaseManager()
        layout = QFormLayout(self)

        self.cmb_item = QComboBox()
        layout.addRow("Ürün:", self.cmb_item)

        self.inp_qty = QLineEdit()
        self.inp_qty.setPlaceholderText("Miktar giriniz")
        layout.addRow("Miktar:", self.inp_qty)

        btn = QPushButton("Oluştur")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        self.load_items()

    def load_items(self):
        """Veritabanından ürünleri yükler"""
        self.db.connect()
        try:
            self.db.cursor.execute("SELECT item_id, item_name FROM items")
            for iid, name in self.db.cursor.fetchall():
                self.cmb_item.addItem(name, iid)
        finally:
            self.db.disconnect()

    def save(self):
        """Yeni talep kaydeder"""
        try:
            qty = float(self.inp_qty.text())
            iid = self.cmb_item.currentData()
            
            self.db.connect()
            # Varsayılan kullanıcı=1, durum='Bekliyor' (ID bulunmalı)
            st_id = self.db.cursor.execute("SELECT status_id FROM request_statuses WHERE status_name='Bekliyor'").fetchone()
            st_id = st_id[0] if st_id else 1 

            self.db.cursor.execute("INSERT INTO purchase_requests (requester_user_id, item_id, quantity, status_id) VALUES (?, ?, ?, ?)", (1, iid, qty, st_id))
            self.db.conn.commit()
            Logger().info(f"Yeni talep oluşturuldu. Ürün ID: {iid}, Miktar: {qty}")
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
            Logger().error(f"Talep oluşturma hatası: {e}")
        finally:
            self.db.disconnect()

class OfferPopup(QDialog):
    def __init__(self, parent=None, request_id=None, item_name="", is_dark=False):
        super().__init__(parent)
        
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        self.setWindowTitle(f"Teklif Oluştur - Talep #{request_id}")
        self.setFixedSize(400, 300)
        self.db = DatabaseManager()
        self.request_id = request_id
        
        layout = QFormLayout(self)
        
        self.lbl_info = QLabel(f"<b>Ürün:</b> {item_name}")
        layout.addRow(self.lbl_info)

        self.cmb_supplier = QComboBox()
        layout.addRow("Tedarikçi:", self.cmb_supplier)

        self.inp_price = QLineEdit()
        self.inp_price.setPlaceholderText("Birim Fiyat")
        layout.addRow("Fiyat:", self.inp_price)

        self.cmb_currency = QComboBox()
        layout.addRow("Para Birimi:", self.cmb_currency)

        btn = QPushButton("Teklifi Kaydet")
        btn.setStyleSheet("background-color: #7C3AED; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        self.load_data()

    def load_data(self):
        self.db.connect()
        try:
            # Suppliers
            self.db.cursor.execute("SELECT supplier_id, company_name FROM suppliers")
            for sid, name in self.db.cursor.fetchall():
                self.cmb_supplier.addItem(name, sid)
                
            # Currencies
            self.db.cursor.execute("SELECT currency_id, code FROM currencies")
            for cid, code in self.db.cursor.fetchall():
                self.cmb_currency.addItem(code, cid)
        finally:
            self.db.disconnect()

    def save(self):
        try:
            price = float(self.inp_price.text().replace(",", "."))
            supplier_id = self.cmb_supplier.currentData()
            currency_id = self.cmb_currency.currentData()
            
            self.db.connect()
            # is_selected = 0 (Hayır)
            self.db.cursor.execute("INSERT INTO offers (request_id, supplier_id, currency_id, price, is_selected) VALUES (?, ?, ?, ?, 0)", 
                                   (self.request_id, supplier_id, currency_id, price))
            self.db.conn.commit()
            
            # Parent logger'a erişmeye çalışalım veya yeni instance
            Logger().info(f"Yeni teklif oluşturuldu. Talep ID: {self.request_id}, Tutar: {price}")
            
            self.accept()
        except ValueError:
             CustomDialogs.warning(self, "Lütfen geçerli bir fiyat giriniz.")
        except Exception as e:
            CustomDialogs.error(self, str(e))
            Logger().error(f"Teklif oluşturma hatası: {e}")
        finally:
            self.db.disconnect()
