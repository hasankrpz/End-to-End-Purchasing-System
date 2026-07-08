from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QDateEdit,
                             QDialog, QFormLayout, QMessageBox, QFrame, 
                             QAbstractItemView)
from utils.table_helper import TableHelper
from utils.text_utils import turkish_lower
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
import sqlite3
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper
from utils.filterable_table import FilterHeader

# Sayısal sıralama için özelleştirilmiş öğe
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        # Eğer her ikisi de sayısal ise sayısal karşılaştırma yap
        try:
            return float(self.text().replace(".", "").replace(",", ".")) < float(other.text().replace(".", "").replace(",", "."))
        except ValueError:
            return super().__lt__(other)

class PageSASTum(QWidget):
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

        # 1. ÜST ÇUBUK (Başlık + Arama + Düğmeler)
        top_bar = QHBoxLayout()

        self.lbl_title = QLabel("Tüm Siparişler")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Sipariş Ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)

        top_bar.addStretch()

        # Düğme Grubu
        self.btn_add = QPushButton("Yeni Sipariş")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_add.clicked.connect(self.open_add_popup)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet("background-color: #f39c12; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_edit.clicked.connect(self.open_edit_popup)

        self.btn_delete = QPushButton("Sil")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet("background-color: #c0392b; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_order)

        top_bar.addWidget(self.btn_add)
        top_bar.addWidget(self.btn_edit)
        top_bar.addWidget(self.btn_delete)

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
        
        # SIRALAMA AYARLARI
        self.table.setSortingEnabled(False) 
        
        self.layout.addWidget(self.table)

        # Verileri Yükle
        self.load_data()

    def update_theme(self, is_dark):
        """Tema değiştiğinde renkleri güncelle"""
        self.is_dark = is_dark
        if is_dark:
            # --- DARK MODE ---
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E5E7EB;") # Gray-200
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
            
            btn_style_base = "QPushButton { padding: 8px 16px; border-radius: 6px; font-weight: bold; color: white; border: 1px solid #374151; }"
            
            self.btn_add.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #065F46; border-color: #059669; }
                QPushButton:hover { background-color: #047857; }
            """)
            self.btn_edit.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #92400E; border-color: #D97706; }
                QPushButton:hover { background-color: #78350F; }
            """)
            self.btn_delete.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #991B1B; border-color: #DC2626; }
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
                QHeaderView {
                    background-color: #1F2937;
                    border: none;
                }
                QHeaderView::section {
                    background-color: #1F2937;
                    color: #9CA3AF;
                    border: none;
                    border-bottom: 2px solid #374151;
                    padding: 4px;
                    font-weight: bold;
                }
                QHeaderView::section:vertical {
                    border-right: 1px solid #374151;
                }
                QTableWidget::item:selected {
                    background-color: #374151;
                    color: white;
                }
                QTableCornerButton::section {
                    background-color: #1F2937;
                    border: none;
                }
            """)
            self.table.setAlternatingRowColors(True)

        else:
            # --- LIGHT MODE ---
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827;") # Gray-900
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

            btn_style_base = "QPushButton { padding: 8px 16px; border-radius: 6px; font-weight: bold; color: white; border: none; }"
            
            self.btn_add.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #10B981; }
                QPushButton:hover { background-color: #059669; }
            """)
            self.btn_edit.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #F59E0B; }
                QPushButton:hover { background-color: #D97706; }
            """)
            self.btn_delete.setStyleSheet(btn_style_base + """
                QPushButton { background-color: #EF4444; }
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
                QTableWidget::item:selected {
                    background-color: #E0E7FF;
                    color: #1E3A8A;
                }
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
        """Veritabanından siparişleri çeker ve tabloya yazar"""
        self.table.setSortingEnabled(False)
        
        search_text = self.search_input.text()
        search_lower = turkish_lower(search_text)

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
            WHERE 1=1
        """
        
        query += " ORDER BY po.order_id DESC"

        self.db.connect()
        try:
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            # SQL ARAMASI YOK - Hepsini getir ve Python'da filtrele Filtresi
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
                    
                    if col_idx in [0, 3, 4, 5]: # ID(0), Miktar(3), Fiyat(4), Toplam(5)
                        display_text = str(val)
                        if col_idx in [4, 5]: # Fiyat formatlama
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
            print(f"Veri yükleme hatası: {e}")
        finally:
            self.db.disconnect()
            self.table.setSortingEnabled(False) # Ekleme sırasında sıralamayı devre dışı bırak

    def delete_order(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            CustomDialogs.warning(self, "Lütfen silinecek bir kayıt seçin.", "Uyarı")
            return
            
        order_id = self.table.item(selected_row, 0).text()
        
        if CustomDialogs.question(self, f"ID: {order_id} nolu siparişi silmek istediğinize emin misiniz?", "Silme Onayı"):
            self.db.connect()
            try:
                status = self.db.cursor.execute("""
                    SELECT s.status_name 
                    FROM purchase_orders po 
                    JOIN order_statuses s ON po.status_id = s.status_id 
                    WHERE po.order_id = ?
                """, (order_id,)).fetchone()
                
                # Varsayılan kullanıcı=1, durum='Bekliyor' (ID bulmalı)
                if status and status[0] == 'Teslim Alındı':
                    CustomDialogs.warning(self, "Teslim alınmış siparişler silinemez!", "İşlem Engellendi")
                    return

                self.db.cursor.execute("DELETE FROM purchase_orders WHERE order_id=?", (order_id,))
                self.db.conn.commit()
                self.logger.info(f"Sipariş silindi. ID: {order_id}")
                CustomDialogs.info(self, "Sipariş silindi.")
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, f"Silme işlemi başarısız: {e}")
                # Üst kaydediciye erişmeye çalışalım veya yeni örnek
                self.logger.error(f"Sipariş silme hatası: {e}")
            finally:
                self.db.disconnect()

    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        dialog = OrderPopup(self, is_dark=is_dark)
        if dialog.exec():
            self.load_data()

    def open_edit_popup(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
             CustomDialogs.warning(self, "Lütfen düzenlenecek bir kayıt seçin.")
             return
        
        order_id = self.table.item(selected_row, 0).text()
        is_dark = getattr(self, 'is_dark', False)
        dialog = OrderPopup(self, order_id, is_dark=is_dark)
        if dialog.exec():
            self.load_data()


class OrderPopup(QDialog):
    def __init__(self, parent=None, order_id=None, is_dark=False):
        super().__init__(parent)
        self.order_id = order_id
        self.is_dark = is_dark
        self.db = DatabaseManager()
        self.logger = Logger()
        
        # Apply Theme
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        self.setWindowTitle("Sipariş Düzenle" if order_id else "Yeni Sipariş")
        
        # Layout Setup
        self.layout = QFormLayout(self)
        
        if self.order_id:
            self.init_edit_ui()
            self.setFixedSize(350, 200)
        else:
            self.init_new_ui()
            self.setFixedSize(400, 500)

    def init_edit_ui(self):
        """Sadece durum değiştirme arayüzü"""
        # 1. Ürün Adı (Sadece Bilgi)
        self.lbl_item_info = QLabel("Yükleniyor...")
        self.lbl_item_info.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addRow("Ürün:", self.lbl_item_info)
        
        # 2. Durum Seçimi
        self.cmb_status = QComboBox()
        self.layout.addRow("Durum:", self.cmb_status)
        
        # Düğmeler
        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Güncelle")
        self.btn_save.clicked.connect(self.save_edit)
        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.clicked.connect(self.close)
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        self.layout.addRow(btn_box)
        
        self.load_edit_data()

    def init_new_ui(self):
        """Yeni sipariş oluşturma arayüzü (Eski hali)"""
        # 0. Mevcut Tekliften Seç
        self.cmb_existing_offers = QComboBox()
        self.cmb_existing_offers.addItem("Lütfen Teklif Seçiniz...", None)
        self.cmb_existing_offers.currentIndexChanged.connect(self.on_offer_selected)
        self.layout.addRow("Mevcut Tekliften:", self.cmb_existing_offers)

        # 1. Ürün Seçimi
        self.cmb_item = QComboBox()
        self.layout.addRow("Ürün:", self.cmb_item)

        # 2. Tedarikçi Seçimi
        self.cmb_supplier = QComboBox()
        self.layout.addRow("Tedarikçi:", self.cmb_supplier)

        # 3. Miktar
        self.inp_quantity = QLineEdit()
        self.inp_quantity.setPlaceholderText("Adet/Miktar")
        self.layout.addRow("Miktar:", self.inp_quantity)

        # 4. Fiyat (Birim)
        self.inp_price = QLineEdit()
        self.inp_price.setPlaceholderText("Birim Fiyat")
        self.layout.addRow("Birim Fiyat:", self.inp_price)

        # 5. Para Birimi
        self.cmb_currency = QComboBox()
        self.layout.addRow("Para Birimi:", self.cmb_currency)

        # 6. Teslim Tarihi
        self.date_delivery = QDateEdit()
        self.date_delivery.setCalendarPopup(True)
        self.date_delivery.setDisplayFormat("yyyy-MM-dd") 
        self.date_delivery.setDate(QDate.currentDate())
        self.layout.addRow("Teslim Tarihi:", self.date_delivery)

        # 7. Durum
        self.cmb_status = QComboBox()
        self.layout.addRow("Durum:", self.cmb_status)

        # Düğmeler
        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.clicked.connect(self.save_new)
        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.clicked.connect(self.close)
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        self.layout.addRow(btn_box)

        self.load_new_data()

    def load_edit_data(self):
        self.db.connect()
        try:
            # Durumları Yükle
            self.db.cursor.execute("SELECT status_id, status_name FROM order_statuses")
            for id, name in self.db.cursor.fetchall():
                self.cmb_status.addItem(name, id)
            
            # Mevcut Veriyi Çek
            query = """
                SELECT i.item_name, Po.status_id
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                WHERE po.order_id = ?
            """
            self.db.cursor.execute(query, (self.order_id,))
            row = self.db.cursor.fetchone()
            if row:
                self.lbl_item_info.setText(row[0])
                
                # Açılır Kutu indeksini bul
                index = self.cmb_status.findData(row[1])
                if index >= 0:
                    self.cmb_status.setCurrentIndex(index)
                    
        except Exception as e:
            print(f"Edit veri yükleme hatası: {e}")
        finally:
            self.db.disconnect()

    def load_new_data(self):
        self.db.connect()
        try:
            # Items
            self.db.cursor.execute("SELECT item_id, item_name FROM items")
            for id, name in self.db.cursor.fetchall():
                self.cmb_item.addItem(name, id)

            # Suppliers
            self.db.cursor.execute("SELECT supplier_id, company_name FROM suppliers")
            for id, name in self.db.cursor.fetchall():
                self.cmb_supplier.addItem(name, id)

            # Currencies
            self.db.cursor.execute("SELECT currency_id, code FROM currencies")
            for id, code in self.db.cursor.fetchall():
                self.cmb_currency.addItem(code, id)
                
            # Statuses
            self.db.cursor.execute("SELECT status_id, status_name FROM order_statuses")
            for id, name in self.db.cursor.fetchall():
                self.cmb_status.addItem(name, id)
                
            # Mevcut Teklifler (Henüz sipariş edilmemiş) - Yalnızca yeni oluşturuluyorsa
            query_offers = """
                SELECT o.offer_id, i.item_name, s.company_name, o.price, c.code, os.status_name
                FROM offers o
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                JOIN suppliers s ON o.supplier_id = s.supplier_id
                JOIN currencies c ON o.currency_id = c.currency_id
                JOIN offer_statuses os ON o.status_id = os.status_id
                LEFT JOIN purchase_orders po ON o.offer_id = po.offer_id
                WHERE po.order_id IS NULL AND os.status_name = 'Bekliyor'
            """
            self.db.cursor.execute(query_offers)
            for row in self.db.cursor.fetchall():
                # Format: "ID: 5 - Ürün (Tedarikçi) - Fiyat [Durum]"
                status_str = row[5]
                display = f"#{row[0]} - {row[1]} ({row[2]}) - {row[3]}{row[4]} [{status_str}]"
                self.cmb_existing_offers.addItem(display, row[0])
            
            # Başlangıç Arayüzü Durum Kontrolü
            self.on_offer_selected()

        except Exception as e:
            print(f"Combo yükleme hatası: {e}")
        finally:
            self.db.disconnect()

    def on_offer_selected(self):
        idx = self.cmb_existing_offers.currentIndex()
        if idx <= 0:
            # Alanları Sıfırla / Etkinleştir
            self.cmb_item.setCurrentIndex(-1)
            self.cmb_supplier.setCurrentIndex(-1)
            self.inp_quantity.clear()
            self.inp_price.clear()
            self.cmb_currency.setCurrentIndex(-1)
            
            self.cmb_item.setEnabled(False)
            self.cmb_supplier.setEnabled(False)
            self.inp_quantity.setEnabled(False)
            self.inp_price.setEnabled(False)
            self.cmb_currency.setEnabled(False)
            return
            
        offer_id = self.cmb_existing_offers.currentData()
        
        self.db.connect()
        try:
            query = """
                SELECT i.item_name, s.company_name, pr.quantity, o.price, c.code
                FROM offers o
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                JOIN suppliers s ON o.supplier_id = s.supplier_id
                JOIN currencies c ON o.currency_id = c.currency_id
                WHERE o.offer_id = ?
            """
            self.db.cursor.execute(query, (offer_id,))
            row = self.db.cursor.fetchone()
            if row:
                self.cmb_item.setCurrentText(row[0])
                self.cmb_supplier.setCurrentText(row[1])
                self.inp_quantity.setText(str(row[2]))
                self.inp_price.setText(str(row[3]))
                self.cmb_currency.setCurrentText(row[4])
                
                # Uyuşmazlığı önlemek için alanları devre dışı bırak
                self.cmb_item.setEnabled(False)
                self.cmb_supplier.setEnabled(False)
                self.inp_quantity.setEnabled(False)
                self.inp_quantity.setReadOnly(True) 
                self.inp_price.setEnabled(True) 
                self.cmb_currency.setEnabled(False)
        except Exception as e:
            print(f"Teklif detay hatası: {e}")
        finally:
            self.db.disconnect()

    def save_edit(self):
        """Sadece durum güncellemesi"""
        status_id = self.cmb_status.currentData()
        
        self.db.connect()
        try:
            update_query = "UPDATE purchase_orders SET status_id = ? WHERE order_id = ?"
            self.db.cursor.execute(update_query, (status_id, self.order_id))
            self.db.conn.commit()
            
            self.logger.info(f"Sipariş durumu güncellendi. ID: {self.order_id} -> StatusID: {status_id}")
            # CustomDialogs.info(self, "Sipariş durumu güncellendi.") # İsteğe bağlı, pencereyi kapatınca tablo yenileniyor zaten
            self.accept()
            
        except Exception as e:
            self.db.conn.rollback()
            CustomDialogs.error(self, f"Güncelleme hatası: {e}")
        finally:
            self.db.disconnect()

    def save_new(self):
        """Yeni sipariş kaydı"""
        try:
            # Doğrula
            try:
                # Miktar devre dışı ama dolu geliyor, Fiyat düzenlenebilir
                # Yine de metin olarak alıp kontrol edelim
                if not self.inp_quantity.text(): raise ValueError
                float(self.inp_quantity.text())
                price = float(self.inp_price.text().replace(",", "."))
            except ValueError:
                CustomDialogs.warning(self, "Miktar ve Fiyat geçerli sayısal değer olmalıdır!")
                return

            status_id = self.cmb_status.currentData()
            date_str = self.date_delivery.date().toString("yyyy-MM-dd")
            selected_offer_id = self.cmb_existing_offers.currentData()
            
            if not selected_offer_id:
                CustomDialogs.warning(self, "Lütfen bir teklif seçiniz.")
                return

            self.db.connect()
            
            # Kur Al
            curr_code_row = self.db.cursor.execute("SELECT c.code FROM offers o JOIN currencies c ON o.currency_id = c.currency_id WHERE o.offer_id=?", (selected_offer_id,)).fetchone()
            ccode = curr_code_row[0] if curr_code_row else 'TRY'
            
            from utils.currency_fetcher import CurrencyFetcher
            rate = CurrencyFetcher.get_rates().get(ccode, 1.0)
            
            # Sipariş Ekle
            ord_query = "INSERT INTO purchase_orders (offer_id, status_id, delivery_date, exchange_rate) VALUES (?, ?, ?, ?)"
            self.db.cursor.execute(ord_query, (selected_offer_id, status_id, date_str, rate))
            
            # Teklif Durumunu & Fiyatını Güncelle
            st_secildi = self.db.cursor.execute("SELECT status_id FROM offer_statuses WHERE status_name='Seçildi'").fetchone()
            if st_secildi:
                 self.db.cursor.execute("UPDATE offers SET status_id=?, price=? WHERE offer_id=?", (st_secildi[0], price, selected_offer_id))

            # Diğerlerini Otomatik Reddet
            req_row = self.db.cursor.execute("SELECT request_id FROM offers WHERE offer_id=?", (selected_offer_id,)).fetchone()
            if req_row:
                req_id = req_row[0]
                st_red = self.db.cursor.execute("SELECT status_id FROM offer_statuses WHERE status_name='Reddedildi'").fetchone()
                if st_red:
                    self.db.cursor.execute("UPDATE offers SET status_id=? WHERE request_id=? AND offer_id!=?", (st_red[0], req_id, selected_offer_id))

            self.db.conn.commit()
            self.logger.info(f"Yeni sipariş eklendi. Teklif ID: {selected_offer_id}")
            self.accept()

        except Exception as e:
            self.db.conn.rollback()
            CustomDialogs.error(self, f"Kayıt hatası: {e}")
            self.logger.error(f"Sipariş kayıt hatası: {e}")
        finally:
            self.db.disconnect()