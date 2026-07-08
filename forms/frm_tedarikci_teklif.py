from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QMessageBox, 
                             QAbstractItemView, QDialog, QFormLayout, QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper
from utils.filterable_table import FilterHeader
from utils.table_helper import TableHelper
from utils.table_helper import TableHelper
from utils.text_utils import turkish_lower
from utils.finance_manager import FinanceManager
from utils.currency_fetcher import CurrencyFetcher

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            val_self = float(self.text().replace(".", "").replace(",", "."))
            val_other = float(other.text().replace(".", "").replace(",", "."))
            return val_self < val_other
        except ValueError:
            return super().__lt__(other)

class PageTedarikciTeklif(QWidget):
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

        # ÜST ÇUBUK
        top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Tedarikçi Teklifleri")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Teklif Ara ...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)

        # self.cmb_filter_status removed here

        top_bar.addStretch()

        self.btn_add = QPushButton("Yeni Teklif")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_popup)
        top_bar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.clicked.connect(self.open_edit_popup)
        top_bar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Sil")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_offer)
        top_bar.addWidget(self.btn_delete)

        self.btn_select = QPushButton("Teklifi Onayla / Seç")
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.clicked.connect(self.select_offer)
        top_bar.addWidget(self.btn_select)

        self.layout.addLayout(top_bar)

        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Teklif ID", "Talep ID", "Ürün", "Tedarikçi", "Fiyat", "Para Birimi", "Durum", "Tarih"])
        
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
            # self.cmb_filter_status.setStyleSheet("padding: 8px; border: 1px solid #4B5563; border-radius: 6px; background-color: #1F2937; color: #F9FAFB;")
            
            button_style_green = """
                QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} 
                QPushButton:hover { background-color: #047857; }
            """
            button_style_blue = """
                QPushButton { background-color: #1E40AF; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #1D4ED8; font-weight: bold;} 
                QPushButton:hover { background-color: #1E3A8A; }
            """
            button_style_orange = """
                QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} 
                QPushButton:hover { background-color: #78350F; }
            """
            button_style_red = """
                QPushButton { background-color: #B91C1C; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} 
                QPushButton:hover { background-color: #991B1B; }
            """

            self.btn_add.setStyleSheet(button_style_green)
            self.btn_select.setStyleSheet(button_style_blue)
            self.btn_edit.setStyleSheet(button_style_orange)
            self.btn_delete.setStyleSheet(button_style_red)
            
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
            # self.cmb_filter_status.setStyleSheet("padding: 8px; border: 1px solid #D1D5DB; border-radius: 6px; background-color: #FFFFFF; color: #111827;")
            
            button_style_green = "QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }"
            button_style_blue = "QPushButton { background-color: #3B82F6; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #2563EB; }"
            button_style_orange = "QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }"
            button_style_red = "QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }"

            self.btn_add.setStyleSheet(button_style_green)
            self.btn_select.setStyleSheet(button_style_blue)
            self.btn_edit.setStyleSheet(button_style_orange)
            self.btn_delete.setStyleSheet(button_style_red)

            self.btn_reset.setStyleSheet("""
                QPushButton { background-color: #6B7280; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} 
                QPushButton:hover { background-color: #4B5563; }
            """)
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
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
        self.table.setSortingEnabled(False)
        search = self.search_input.text()
        search_lower = turkish_lower(search)
        
        # NOTE: Added pr.quantity back based on assumption it's needed for table display
        query = """
            SELECT 
                o.offer_id,
                o.request_id,
                i.item_name,
                s.company_name,
                o.price,
                c.code,
                os.status_name,
                o.created_at
            FROM offers o
            JOIN purchase_requests pr ON o.request_id = pr.request_id
            JOIN items i ON pr.item_id = i.item_id
            JOIN suppliers s ON o.supplier_id = s.supplier_id
            JOIN currencies c ON o.currency_id = c.currency_id
            JOIN offer_statuses os ON o.status_id = os.status_id
            WHERE 1=1
        """
        
        query += " ORDER BY o.offer_id DESC"

        self.db.connect()
        try:
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            # Python Filter
            filtered_rows = []
            if search:
                for row in rows:
                    row_text = " ".join([str(val) for val in row if val is not None])
                    if search_lower in turkish_lower(row_text):
                        filtered_rows.append(row)
            else:
                filtered_rows = rows
                
            self.table.setRowCount(0)
            self.table.setSortingEnabled(False) # Disable sorting while inserting
            for r_idx, row in enumerate(filtered_rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    if c_idx == 6: # Durum (status_name)
                        # Renklendirme yapılabilir
                        item = QTableWidgetItem(str(val))
                        if val == 'Reddedildi':
                            item.setForeground(QColor('red'))
                        elif val == 'Seçildi':
                            item.setForeground(QColor('green'))
                    elif c_idx == 4: # Fiyat Formatsız
                         display_text = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
                         item = NumericTableWidgetItem(display_text)
                    elif c_idx in [0, 3]: # OfferID(0), Miktar(3) -> Numeric
                        item = NumericTableWidgetItem(str(val))
                    else:
                        item = QTableWidgetItem(str(val))
                    
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)

            # Vurgula
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

    def select_offer(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen onaylanacak teklifi seçin.", "Uyarı")
            return

        offer_id = self.table.item(row, 0).text()
        status_text = self.table.item(row, 6).text()
        
        if status_text == "Seçildi":
             CustomDialogs.warning(self, "Bu teklif zaten seçilmiş.")
             return

        self.db.connect()
        try:
            # Kara Liste Durumunu Kontrol Et
            # Tekliften tedarikçi_id sorgula -> sonra tedarikçinin black_list durumunu kontrol et
            query_check = """
                SELECT s.black_list, s.company_name, ss.status_name
                FROM offers o 
                JOIN suppliers s ON o.supplier_id = s.supplier_id 
                JOIN supplier_statuses ss ON s.status_id = ss.status_id
                WHERE o.offer_id = ?
            """
            r_check = self.db.cursor.execute(query_check, (offer_id,)).fetchone()
            
            confirm_msg = "Bu teklifi onaylayıp siparişe dönüştürmek istiyor musunuz?"
            
            if r_check:
                is_bl = r_check[0] == 1
                comp_name = r_check[1]
                status_name = r_check[2]
                
                if status_name == 'Pasif':
                    # Pasif uyarısı - İşlem Engellensin mi? Kullanıcı "Uyarı çıkar" dedi.
                    # Genelde pasif tedarikçiden alım yapılmaz.
                    CustomDialogs.warning(self, f"'{comp_name}' firması PASİF durumda!\n\nBu tedarikçiden sipariş oluşturamazsınız.", "İşlem Engellendi")
                    return

                if is_bl: # Blacklisted
                    confirm_msg = f"DİKKAT! '{comp_name}' firması KARA LİSTEDE!\n\nYine de bu teklifi onaylayıp sipariş vermek istiyor musunuz?"
                    if not CustomDialogs.question(self, confirm_msg, "Kritik Uyarı"):
                        return
                else:
                     if not CustomDialogs.question(self, confirm_msg, "Onay"):
                        return

            # Devam et
            
            # --- BÜTÇE KONTROLÜ BAŞLANGIÇ ---
            finance_mgr = FinanceManager()
            
            # 1. Departman ve Maliyet Bilgisini Al
            budget_info = self.db.cursor.execute("""
                SELECT u.department_id, o.price * pr.quantity
                FROM offers o
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN users u ON pr.requester_user_id = u.user_id
                WHERE o.offer_id=?
            """, (offer_id,)).fetchone()
            
            if budget_info:
                dept_id = budget_info[0]
                cost = budget_info[1]
                
                is_ok, msg, code = finance_mgr.check_budget_availability(dept_id, cost)
                if not is_ok:
                    # WARN POLICY
                    warn_msg = f"BÜTÇE UYARISI!\n\n{msg}\n\nYine de siparişi onaylamak istiyor musunuz?"
                    if not CustomDialogs.question(self, warn_msg, "Bütçe Aşımı"):
                        return
            # --- BÜTÇE KONTROLÜ BİTİŞ ---

            # 1. Teklifi Güncelle (Seçilen için Durum ID'sini Al)
            st_secildi = self.db.cursor.execute("SELECT status_id FROM offer_statuses WHERE status_name='Seçildi'").fetchone()[0]
            self.db.cursor.execute("UPDATE offers SET status_id=? WHERE offer_id=?", (st_secildi, offer_id))
            
            # Bu teklif için zaten bir sipariş var mı kontrol et
            exist = self.db.cursor.execute("SELECT order_id FROM purchase_orders WHERE offer_id=?", (offer_id,)).fetchone()
            
            if not exist:
                import datetime
                today_date = datetime.date.today().strftime("%Y-%m-%d")
                st = self.db.cursor.execute("SELECT status_id FROM order_statuses WHERE status_name='Hazırlanıyor'").fetchone()
                order_status_id = st[0] if st else 1

                # Döviz Kurunu Yakala
                # 1. Para Birimi Kodunu Al
                curr_row = self.db.cursor.execute("SELECT c.code FROM offers o JOIN currencies c ON o.currency_id = c.currency_id WHERE o.offer_id=?", (offer_id,)).fetchone()
                currency_code = curr_row[0] if curr_row else "TRY"
                
                # 2. Kuru Al
                rates = CurrencyFetcher.get_rates()
                exchange_rate = rates.get(currency_code, 1.0)

                self.db.cursor.execute("INSERT INTO purchase_orders (offer_id, status_id, delivery_date, exchange_rate) VALUES (?, ?, ?, ?)", 
                                       (offer_id, order_status_id, today_date, exchange_rate))
                
                # Talep Durumunu 'Tamamlandı' (4) Olarak Güncelle
                req_id_row = self.db.cursor.execute("SELECT request_id FROM offers WHERE offer_id=?", (offer_id,)).fetchone()
                if req_id_row:
                    req_id = req_id_row[0]
                    self.db.cursor.execute("UPDATE purchase_requests SET status_id=4 WHERE request_id=?", (req_id,))
                    self.logger.info(f"Talep durumu Tamamlandı (4) yapıldı. Talep ID: {req_id}")

                    # --- OTOMATİK REDDETME MANTIĞI (frm_sas_tum dosyasından kopyalandı) ---
                    st_red = self.db.cursor.execute("SELECT status_id FROM offer_statuses WHERE status_name='Reddedildi'").fetchone()
                    if st_red:
                        st_reddedildi = st_red[0]
                        self.db.cursor.execute("UPDATE offers SET status_id=? WHERE request_id=? AND offer_id!=?", (st_reddedildi, req_id, offer_id))
                        self.logger.info(f"Diğer teklifler otomatik reddedildi. ReqID: {req_id}")
                    # -------------------------------------------------------

                self.logger.info(f"Teklif onaylandı ve sipariş oluşturuldu. Teklif ID: {offer_id}, Kur: {exchange_rate}")
            
            self.db.conn.commit()
            CustomDialogs.info(self, "Teklif onaylandı ve sipariş oluşturuldu.")
            self.load_data()
            
        except Exception as e:
            self.db.conn.rollback()
            CustomDialogs.error(self, str(e))
            self.logger.error(f"Teklif onaylama hatası: {e}")
        finally:
            self.db.disconnect()

    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        d = OfferPopup(self, is_dark=is_dark)
        if d.exec(): self.load_data()

    def open_edit_popup(self):
        row = self.table.currentRow()
        if row < 0: return CustomDialogs.warning(self, "Lütfen düzenlenecek teklifi seçin.")
        
        offer_id = self.table.item(row, 0).text()
        is_dark = getattr(self, 'is_dark', False)
        d = OfferPopup(self, offer_id, is_dark=is_dark)
        if d.exec(): self.load_data()

    def delete_offer(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen silinecek teklifi seçin.")
            return

        offer_id = self.table.item(row, 0).text()
        
        # Seçilmiş bir teklif mi?
        status_text = self.table.item(row, 6).text()
        if status_text == "Seçildi":
            CustomDialogs.warning(self, "Seçilmiş (Siparişleşmiş) bir teklifi silemezsiniz! Önce siparişi iptal etmelisiniz.")
            return

        if not CustomDialogs.question(self, "Bu teklifi silmek istediğinize emin misiniz?", "Silme Onayı"):
            return
            
        self.db.connect()
        try:
            self.db.cursor.execute("DELETE FROM offers WHERE offer_id=?", (offer_id,))
            self.db.conn.commit()
            
            self.logger.info(f"Teklif silindi. ID: {offer_id}")
            CustomDialogs.info(self, "Teklif silindi.")
            self.load_data()
        except Exception as e:
            self.db.conn.rollback()
            CustomDialogs.error(self, f"Silme hatası: {str(e)}")
        finally:
            self.db.disconnect()


class OfferPopup(QDialog):
    def __init__(self, parent=None, offer_id=None, is_dark=False):
        super().__init__(parent)
        
        # Temayı Uygula
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        self.setWindowTitle("Teklif İşlemleri")
        self.setFixedSize(400, 350)
        self.offer_id = offer_id
        self.db = DatabaseManager()
        
        layout = QFormLayout(self)
        
        # Alanlar
        self.cmb_request = QComboBox()
        self.cmb_supplier = QComboBox()
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setRange(0, 10000000)
        self.spin_price.setDecimals(2)
        self.cmb_currency = QComboBox()
        
        layout.addRow("Talep (Ürün):", self.cmb_request)
        layout.addRow("Tedarikçi:", self.cmb_supplier)
        layout.addRow("Fiyat:", self.spin_price)
        layout.addRow("Para Birimi:", self.cmb_currency)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)
        
        # Verileri Yükle
        self.load_dropdowns()
        
        if self.offer_id:
            self.load_details()

    def load_dropdowns(self):
        self.db.connect()
        try:
            # 1. Tedarikçiler
            self.db.cursor.execute("SELECT supplier_id, company_name FROM suppliers")
            for id, name in self.db.cursor.fetchall():
                self.cmb_supplier.addItem(name, id)
                
            # 2. Para Birimleri
            self.db.cursor.execute("SELECT currency_id, code FROM currencies")
            for id, code in self.db.cursor.fetchall():
                self.cmb_currency.addItem(code, id)
        except Exception as e:
            print(f"Dropdown load error: {e}")
        finally:
            self.db.disconnect()
        
        # 3. Talep (Özel Yükleme)
        self.load_requests_combo()

    def load_requests_combo(self):
        self.db.connect()
        try:
            # Sadece statüsü uygun olan talepler veya hepsi? Şimdilik hepsi
            query = """
                SELECT pr.request_id, i.item_name, pr.quantity
                FROM purchase_requests pr
                JOIN items i ON pr.item_id = i.item_id
                JOIN request_statuses s ON pr.status_id = s.status_id
                WHERE s.status_name = 'Onaylandı'
                ORDER BY pr.request_id DESC
            """
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            self.cmb_request.clear()
            for r in rows:
                display_text = f"[{r[0]}] {r[1]} ({r[2]} Adet)" 
                self.cmb_request.addItem(display_text, r[0])
        except Exception as e:
            print(f"Request combo load error: {e}")
        finally:
            self.db.disconnect()

    def load_details(self):
        self.db.connect()
        try:
            r = self.db.cursor.execute("SELECT request_id, supplier_id, price, currency_id FROM offers WHERE offer_id=?", (self.offer_id,)).fetchone()
            if r:
                # Talep Seç
                idx = self.cmb_request.findData(r[0])
                if idx >= 0: self.cmb_request.setCurrentIndex(idx)
                
                # Tedarikçi Seç
                idx = self.cmb_supplier.findData(r[1])
                if idx >= 0: self.cmb_supplier.setCurrentIndex(idx)
                
                self.spin_price.setValue(r[2])
                
                # Para Birimi Seç
                idx = self.cmb_currency.findData(r[3])
                if idx >= 0: self.cmb_currency.setCurrentIndex(idx)
        finally:
            self.db.disconnect()

    def save(self):
        try:
            req_id = self.cmb_request.currentData()
            supp_id = self.cmb_supplier.currentData()
            price = self.spin_price.value()
            curr_id = self.cmb_currency.currentData()
            
            if not req_id or not supp_id or not curr_id:
                CustomDialogs.warning(self, "Lütfen tüm alanları seçiniz.")
                return

            self.db.connect()
            if self.offer_id:
                # GÜNCELLE
                self.db.cursor.execute("UPDATE offers SET request_id=?, supplier_id=?, price=?, currency_id=? WHERE offer_id=?", 
                                       (req_id, supp_id, price, curr_id, self.offer_id))
                Logger().info(f"Teklif güncellendi. ID: {self.offer_id}")
            else:
                # EKLE (Varsayılan Durum: Bekliyor)
                st_bekliyor = self.db.cursor.execute("SELECT status_id FROM offer_statuses WHERE status_name='Bekliyor'").fetchone()[0]
                self.db.cursor.execute("INSERT INTO offers (request_id, supplier_id, price, currency_id, status_id) VALUES (?, ?, ?, ?, ?)",
                                       (req_id, supp_id, price, curr_id, st_bekliyor))
                Logger().info("Yeni teklif eklendi.")

            self.db.conn.commit()
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
            Logger().error(f"Teklif kaydetme hatası: {e}")
        finally:
            self.db.disconnect()
