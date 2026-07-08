from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QComboBox, QDialog, QFormLayout, 
                             QDateEdit, QDoubleSpinBox, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.table_helper import TableHelper
from utils.filterable_table import FilterHeader
from utils.text_utils import turkish_lower
from utils.theme_helper import ThemeHelper
from utils.currency_fetcher import CurrencyFetcher

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            val_self = float(self.text().replace(".", "").replace(",", "."))
            val_other = float(other.text().replace(".", "").replace(",", "."))
            return val_self < val_other
        except ValueError:
            return super().__lt__(other)

class PageInvoices(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logger = Logger()
        self.init_ui()

    def showEvent(self, event):
        self.load_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # 1. ÜST ÇUBUK
        top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Fatura Yönetimi")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Fatura Ara ...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top_bar.addWidget(self.btn_reset)
        
        top_bar.addStretch()
        
        self.btn_add = QPushButton("Siparişten Oluştur")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_dialog)
        top_bar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        top_bar.addWidget(self.btn_edit)
        
        self.btn_del = QPushButton("Sil")
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.clicked.connect(self.delete_invoice)
        top_bar.addWidget(self.btn_del)

        self.layout.addLayout(top_bar)
        
        # 2. TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Fatura No", "Tedarikçi", "Tarih", "Son Ödeme", "Tutar", "Durum"])
        
        # Filtre Başlığı
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
            
            button_style_green = "QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} QPushButton:hover { background-color: #047857; }"
            button_style_orange = "QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} QPushButton:hover { background-color: #78350F; }"
            button_style_red = "QPushButton { background-color: #B91C1C; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} QPushButton:hover { background-color: #991B1B; }"
            
            self.btn_add.setStyleSheet(button_style_green)
            self.btn_edit.setStyleSheet(button_style_orange)
            self.btn_del.setStyleSheet(button_style_red)

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
            
            button_style_green = "QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }"
            button_style_orange = "QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }"
            button_style_red = "QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }"

            self.btn_add.setStyleSheet(button_style_green)
            self.btn_edit.setStyleSheet(button_style_orange)
            self.btn_del.setStyleSheet(button_style_red)
            
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
        self.search_input.clear()
        if hasattr(self, 'filter_header'):
            self.filter_header.clear_filters()
        self.load_data()

    def load_data(self):
        self.table.setSortingEnabled(False)
        search = self.search_input.text()
        search_lower = turkish_lower(search)
        
        self.db.connect()
        try:
            query = """
                SELECT i.invoice_id, i.invoice_no, s.company_name, i.invoice_date, i.due_date, i.total_amount, ist.status_name
                FROM invoices i
                JOIN suppliers s ON i.supplier_id = s.supplier_id
                LEFT JOIN invoice_statuses ist ON i.status_id = ist.status_id
                ORDER BY i.invoice_id DESC
            """
            rows = self.db.cursor.execute(query).fetchall()
            
            filtered_rows = []
            if search:
                for row in rows:
                    row_text = " ".join([str(val) for val in row if val is not None])
                    if search_lower in turkish_lower(row_text):
                        filtered_rows.append(row)
            else:
                filtered_rows = rows

            self.table.setRowCount(0)
            for r_idx, row in enumerate(filtered_rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    display_val = str(val) if val is not None else ""
                    
                    if c_idx == 5: # Tutar
                         display_val = f"{val:,.2f}"
                         item = NumericTableWidgetItem(display_val)
                    elif c_idx in [0]: # ID
                         item = NumericTableWidgetItem(display_val)
                    else:
                         item = QTableWidgetItem(display_val)
                    
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)
            
            # Vurgula
            is_dark = getattr(self, 'is_dark', False)
            TableHelper.highlight_search_results(self.table, search, is_dark)
            
            # Filtreleri Tekrar Uygula
            if hasattr(self.table.horizontalHeader(), 'apply_filters'):
                self.table.horizontalHeader().apply_filters()

        finally:
            self.db.disconnect()
            self.table.setSortingEnabled(False)

    def open_add_dialog(self):
        d = InvoiceDialog(self)
        if d.exec():
            self.load_data()

    def open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek faturayı seçin.")
            return
        
        inv_id = self.table.item(row, 0).text()
        
        # Durum Kontrolü (İsteğe bağlı - örneğin ödenmiş faturalar düzenlenememelidir)
        # Şimdilik düzenlemeye izin ver
        
        d = InvoiceDialog(self, invoice_id=inv_id)
        if d.exec():
            self.load_data()

    def delete_invoice(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen silinecek faturayı seçin.")
            return

        inv_id = self.table.item(row, 0).text()
        
        self.db.connect()
        try:
            # 1. Veritabanı Kontrolü: Ödeme var mı?
            # Durum 'BEKLİYOR' olsa bile gerçek tabloyu kontrol et.
            count = self.db.cursor.execute("SELECT count(*) FROM payments WHERE invoice_id=?", (inv_id,)).fetchone()[0]
            
            if count > 0:
                CustomDialogs.warning(self, f"Bu faturaya ait {count} adet ödeme kaydı bulundu!\n\nVeri bütünlüğü için önce ödemeleri silmelisiniz.", "Silinemez")
                return

            if CustomDialogs.question(self, f"ID: {inv_id} nolu faturayı silmek istediğinize emin misiniz?", "Sil"):
                self.db.cursor.execute("DELETE FROM invoices WHERE invoice_id=?", (inv_id,))
                self.db.conn.commit()
                self.logger.info(f"Fatura silindi. ID: {inv_id}")
                CustomDialogs.info(self, "Fatura silindi.")
                self.load_data()
        except Exception as e:
            self.db.conn.rollback()
            self.logger.error(f"Fatura silinirken hata: {e}")
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()


class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_id=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        
        title = "Sipariş Faturalandır" if not invoice_id else "Fatura Düzenle"
        self.setWindowTitle(title)
        self.setFixedWidth(500)
        self.db = DatabaseManager()
        self.logger = Logger()
        
        # Temayı Uygula
        is_dark = getattr(parent, 'is_dark', False) if parent else False
        self.is_dark = is_dark
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.cmb_order = QComboBox()
        self.load_orders() # Doldur ve muhtemelen seç
        
        # Düzenliyorsak, Sipariş değişikliğini devre dışı mı bırakalım?
        # Veya zaten siparişe bağlı mevcut bir faturayı düzenliyorsak
        
        self.inp_no = QLineEdit()
        self.inp_date = QDateEdit(QDate.currentDate())
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setEnabled(False) # Kullanıcı değiştiremesin
        self.inp_date.setStyleSheet("color: black; background-color: #f3f4f6;") # Disabled ama okunur olsun

        self.inp_due = QDateEdit(QDate.currentDate().addDays(30))
        self.inp_due.setCalendarPopup(True)
        
        self.spn_subtotal = QDoubleSpinBox()
        self.spn_subtotal.setRange(0, 10000000)
        self.spn_subtotal.setPrefix("₺ ")
        self.spn_subtotal.setReadOnly(True) # Sadece programatik
        self.spn_subtotal.setStyleSheet("font-weight: bold; background-color: #f3f4f6; color: black;")
        self.spn_subtotal.valueChanged.connect(self.calculate_total)
        
        self.spn_tax_rate = QDoubleSpinBox()
        self.spn_tax_rate.setRange(0, 100)
        self.spn_tax_rate.setSuffix(" %")
        self.spn_tax_rate.setValue(20) # Default KDV
        self.spn_tax_rate.valueChanged.connect(self.calculate_total)
        
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 10000000)
        self.spn_amount.setPrefix("₺ ")
        self.spn_amount.setReadOnly(True) # Otomatik hesaplanan
        self.spn_amount.setStyleSheet("font-weight: bold; background-color: #f3f4f6; color: black;")
        
        form.addRow("Sipariş Seç:", self.cmb_order)
        form.addRow("Fatura No:", self.inp_no)
        form.addRow("Fatura Tarihi:", self.inp_date)
        form.addRow("Son Ödeme:", self.inp_due)
        form.addRow("Ara Toplam:", self.spn_subtotal)
        form.addRow("KDV Oranı:", self.spn_tax_rate)
        form.addRow("GENEL TOPLAM:", self.spn_amount)
        
        layout.addLayout(form)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        
        # Mantıksal Özellikler
        if not self.invoice_id:
            self.cmb_order.currentIndexChanged.connect(self.on_order_change)
        else:
            self.load_invoice_data()

    def load_orders(self):
        self.db.connect()
        try:
            # Yeni oluşturuluyorsa, sadece faturasız siparişleri mi göster? Yoksa tüm teslim edilenleri mi?
            # İdeal Olan: Henüz tam faturalandırılmamış, teslim alınan siparişler.
            # Basitleştirilmiş: Tüm Teslim Alınan siparişler.
            
            # Düzenliyorsak, mevcut siparişin de listede olması gerekir (faturası olsa bile - yani bu fatura)
            
            query = """
                SELECT po.order_id, s.company_name, i.item_name, (o.price * pr.quantity) as total
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN suppliers s ON o.supplier_id = s.supplier_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                JOIN order_statuses os ON po.status_id = os.status_id
                WHERE os.status_name = 'Teslim Alındı'
                AND (po.order_id NOT IN (SELECT order_id FROM invoices WHERE order_id IS NOT NULL) 
                     OR po.order_id IN (SELECT order_id FROM invoices WHERE invoice_id = ?))
            """
            # invoice_id için olası None durumunu güvenle ele al (SQLite genelde eşleşme yoksa null olarak ele alır)
            p_id = self.invoice_id if self.invoice_id else -1
            rows = self.db.cursor.execute(query, (p_id,)).fetchall()
            
            self.cmb_order.clear()
            # Yer tutucu ekle
            self.cmb_order.addItem("Seçiniz...", None)
            
            for r in rows:
                txt = f"Order #{r[0]} - {r[1]} - {r[2]} ({r[3]:,.2f} TL)"
                self.cmb_order.addItem(txt, {"id": r[0], "total": r[3], "supplier": r[1]})
        finally:
            self.db.disconnect()

    def calculate_total(self):
        sub = self.spn_subtotal.value()
        rate = self.spn_tax_rate.value()
        tax_amt = sub * (rate / 100)
        total = sub + tax_amt
        self.spn_amount.setValue(total)

    def on_order_change(self):
        data = self.cmb_order.currentData()
        if data:
            # Şimdilik Sipariş Toplamını Ara Toplam mı varsay? Yoksa Toplam mı?
            # Genelde sipariş toplamdır. Gerekirse vergiyi ters hesaplayalım mı, yoksa ara toplam = toplam ve vergi 0 mı yapalım?
            # Daha iyisi: Başlangıçta Ara Toplam = Toplam, Vergi = 0 ayarla, tam miktarla eşleşsin.
            # Kullanıcı bölmek isterse ayarlayabilir.
            self.spn_subtotal.setValue(data["total"])
            self.spn_tax_rate.setValue(0) 

    def load_invoice_data(self):
        self.db.connect()
        try:
            r = self.db.cursor.execute("SELECT invoice_no, invoice_date, due_date, total_amount, tax_amount FROM invoices WHERE invoice_id=?", (self.invoice_id,)).fetchone()
            if r:
                self.inp_no.setText(str(r[0]))
                self.inp_date.setDate(QDate.fromString(r[1], "yyyy-MM-dd"))
                self.inp_due.setDate(QDate.fromString(r[2], "yyyy-MM-dd"))
                
                total = r[3]
                tax_amt = r[4] if r[4] else 0.0
                subtotal = total - tax_amt
                
                # Yaklaşık oran
                if subtotal > 0:
                    rate = (tax_amt / subtotal) * 100
                else:
                    rate = 0
                
                self.spn_subtotal.setValue(subtotal)
                self.spn_tax_rate.setValue(rate)
                self.spn_amount.setValue(total) # Otomatik güncellenmeli ama açıkça ayarla
                
                self.cmb_order.setEnabled(False)
        finally:
            self.db.disconnect()

    def save(self):
        self.db.connect()
        try:
            total = self.spn_amount.value()
            sub = self.spn_subtotal.value()
            tax_amt = total - sub
            
            if self.invoice_id:
                 self.db.cursor.execute("""
                    UPDATE invoices SET invoice_no=?, invoice_date=?, due_date=?, total_amount=?, tax_amount=?
                    WHERE invoice_id=?
                 """, (self.inp_no.text(), self.inp_date.date().toString("yyyy-MM-dd"), self.inp_due.date().toString("yyyy-MM-dd"), total, tax_amt, self.invoice_id))
            else:
                data = self.cmb_order.currentData()
                if not data: 
                    CustomDialogs.warning(self, "Lütfen bir sipariş seçiniz.")
                    return
                order_id = data["id"]
                
                supp_row = self.db.cursor.execute("""
                    SELECT o.supplier_id FROM purchase_orders po 
                    JOIN offers o ON po.offer_id = o.offer_id 
                    WHERE po.order_id=?
                """, (order_id,)).fetchone()
                
                if not supp_row: return
                supp_id = supp_row[0]
                
                # Fatura Tarihindeki Kuru Yakala (Şimdilik Güncel Kura Yaklaşık veya gerekirse geçmişi getir)
                # İdealde fatura tarihi için kur çekmeliyiz ama CurrencyFetcher güncel kuru alır.
                # Plana göre güncel kuru kullanalım.
                rates = CurrencyFetcher.get_rates()
                
                # Para birimi koduna ihtiyacımız var. Çekelim.
                curr_row = self.db.cursor.execute("""
                    SELECT c.code 
                    FROM purchase_orders po 
                    JOIN offers o ON po.offer_id = o.offer_id 
                    JOIN currencies c ON o.currency_id = c.currency_id
                    WHERE po.order_id=?
                """, (order_id,)).fetchone()
                curr_code = curr_row[0] if curr_row else 'TRY'
                exchange_rate = rates.get(curr_code, 1.0)
                
                status_bekliyor = 2
                self.db.cursor.execute("""
                    INSERT INTO invoices (invoice_no, supplier_id, invoice_date, due_date, total_amount, tax_amount, status_id, exchange_rate, order_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.inp_no.text(), supp_id, self.inp_date.date().toString("yyyy-MM-dd"), self.inp_due.date().toString("yyyy-MM-dd"), total, tax_amt, status_bekliyor, exchange_rate, order_id))
                
            self.db.conn.commit()
            
            action = "güncellendi" if self.invoice_id else "oluşturuldu"
            self.logger.info(f"Fatura {action}. No: {self.inp_no.text()}")
            
            CustomDialogs.info(self, "Fatura kaydedildi.")
            self.accept()
        except Exception as e:
            self.logger.error(f"Fatura kaydedilirken hata: {e}")
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()
