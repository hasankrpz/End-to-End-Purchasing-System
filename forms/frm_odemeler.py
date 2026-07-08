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

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            val_self = float(self.text().replace(".", "").replace(",", "."))
            val_other = float(other.text().replace(".", "").replace(",", "."))
            return val_self < val_other
        except ValueError:
            return super().__lt__(other)

class PagePayments(QWidget):
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
        
        # ÜST ÇUBUK
        top = QHBoxLayout()
        self.lbl_title = QLabel("Ödeme Yönetimi")
        self.lbl_title.setObjectName("PageTitle")
        top.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ödeme Ara ...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.load_data)
        top.addWidget(self.search_input)

        self.btn_reset = QPushButton("Filtreyi Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        top.addWidget(self.btn_reset)
        
        top.addStretch()
        
        self.btn_pay = QPushButton("Ödeme Yap")
        self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pay.clicked.connect(self.open_pay_dialog)
        top.addWidget(self.btn_pay)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        top.addWidget(self.btn_edit)
        
        self.btn_del = QPushButton("Sil")
        self.btn_del.clicked.connect(self.delete_payment)
        top.addWidget(self.btn_del)
        
        self.layout.addLayout(top)
        
        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Ödeme ID", "Fatura No", "Tedarikçi", "Tarih", "Tutar", "Yöntem"])
        
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
            
            self.btn_pay.setStyleSheet(button_style_green)
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

            self.btn_pay.setStyleSheet(button_style_green)
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
                SELECT p.payment_id, i.invoice_no, s.company_name, p.payment_date, p.amount, p.payment_method
                FROM payments p
                JOIN invoices i ON p.invoice_id = i.invoice_id
                JOIN suppliers s ON i.supplier_id = s.supplier_id
                ORDER BY p.payment_id DESC
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
                    
                    if c_idx == 4: # Tutar
                        display_val = f"{val:,.2f}"
                        item = NumericTableWidgetItem(display_val)
                    elif c_idx == 0:
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

    def open_pay_dialog(self):
        d = PaymentDialog(self)
        if d.exec():
            self.load_data()

    def open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek ödemeyi seçin.")
            return
        
        pay_id = self.table.item(row, 0).text()
        d = PaymentDialog(self, payment_id=pay_id)
        if d.exec():
            # Fatura Durum Mantığını Güncelle (Yeniden Hesapla) kaydetme işleminde ele alınır
            self.load_data()

    def delete_payment(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen silinecek ödemeyi seçin.")
            return

        pay_id = self.table.item(row, 0).text()
        
        if CustomDialogs.question(self, f"ID: {pay_id} nolu ödemeyi silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                # 1. Daha sonra durum güncellemesi için fatura ID'sini al
                inv_id_row = self.db.cursor.execute("SELECT invoice_id FROM payments WHERE payment_id=?", (pay_id,)).fetchone()
                
                # 2. Sil
                self.db.cursor.execute("DELETE FROM payments WHERE payment_id=?", (pay_id,))
                
                # 3. Fatura Durumunu Güncelle
                if inv_id_row:
                    inv_id = inv_id_row[0]
                    total = self.db.cursor.execute("SELECT total_amount FROM invoices WHERE invoice_id=?", (inv_id,)).fetchone()[0]
                    paid_sum = self.db.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id=?", (inv_id,)).fetchone()[0]
                    
                    new_status = 2 # Bekliyor
                    if paid_sum >= total:
                        new_status = 1 # Ödendi
                    elif paid_sum > 0:
                        new_status = 3 # Kısmi
                    
                    self.db.cursor.execute("UPDATE invoices SET status_id=? WHERE invoice_id=?", (new_status, inv_id))
                
                self.db.conn.commit()
                self.logger.info(f"Ödeme silindi. ID: {pay_id}")
                CustomDialogs.info(self, "Ödeme silindi.")
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                self.logger.error(f"Ödeme silinirken hata: {e}")
                CustomDialogs.error(self, str(e))
            finally:
                self.db.disconnect()


class PaymentDialog(QDialog):
    def __init__(self, parent=None, payment_id=None):
        super().__init__(parent)
        self.payment_id = payment_id
        
        title = "Ödeme Girişi" if not payment_id else "Ödeme Düzenle"
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.db = DatabaseManager()
        self.logger = Logger()
        
        # Temayı Uygula
        is_dark = getattr(parent, 'is_dark', False) if parent else False
        self.is_dark = is_dark
        ThemeHelper.apply_popup_theme(self, is_dark)

        layout = QFormLayout(self)
        
        self.cmb_invoice = QComboBox()
        self.load_invoices()
        
        self.inp_date = QDateEdit(QDate.currentDate())
        self.inp_date.setCalendarPopup(True)
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 10000000)
        self.cmb_method = QComboBox()
        
        # Ödeme yöntemlerini veritabanından yükle
        self.load_payment_methods()
        
        if not self.payment_id:
            self.cmb_invoice.currentIndexChanged.connect(self.on_invoice_change)
        
        layout.addRow("Fatura Seç:", self.cmb_invoice)
        layout.addRow("Ödeme Tarihi:", self.inp_date)
        layout.addRow("Tutar:", self.spn_amount)
        layout.addRow("Yöntem:", self.cmb_method)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)
        
        if self.payment_id:
            self.load_payment_data()
    
    def load_payment_methods(self):
        """Ödeme yöntemlerini veritabanından yükle"""
        self.db.connect()
        try:
            rows = self.db.cursor.execute("SELECT method_name FROM payment_methods ORDER BY method_id").fetchall()
            self.cmb_method.clear()
            for row in rows:
                self.cmb_method.addItem(row[0])
        finally:
            self.db.disconnect()

    def load_invoices(self):
        self.db.connect()
        try:
            # Düzenliyorsak, tamamen ödenmiş olsa bile mevcut faturayı dahil etmeliyiz
            # Yeni ise, sadece kalan bakiyesi olanları göster
            
            if self.payment_id:
                # Tüm Faturaları Yükle (veya sadece ilgili olanı? Tümü combo için daha kolay)
                # Ancak performans ve mantık için tüm 'ilgili' olanları yükleyelim
                 query = "SELECT invoice_id, invoice_no, total_amount FROM invoices"
            else:
                query = """
                    SELECT invoice_id, invoice_no, total_amount, supplier_id,
                        (SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id=invoices.invoice_id) as paid
                    FROM invoices 
                    WHERE status_id != 1
                """
                
            rows = self.db.cursor.execute(query).fetchall()
            
            self.cmb_invoice.clear()
            for r in rows:
                inv_id = r[0]
                no = r[1]
                total = r[2] or 0
                
                # Sorgu 'yeni' olan ise döngü içinde kalanı hesapla
                if len(r) > 3:
                    paid = r[4] or 0
                    remaining = total - paid
                else: 
                     # Düzenleme modu için, daha fazla sorgu veya mantık olmadan kalanı kolayca hesaplayamayız.
                     # Sadece Fatura No ve Toplamı göster
                    remaining = 0 # Yer Tutucu
                    
                if self.payment_id:
                     txt = f"{no} (Top: {total:,.2f})"
                     self.cmb_invoice.addItem(txt, {"id": inv_id})
                else:
                    if round(remaining, 2) > 0:
                        txt = f"{no} (Kalan: {remaining:,.2f} TL)"
                        self.cmb_invoice.addItem(txt, {"id": inv_id, "remaining": remaining})
        finally:
            self.db.disconnect()

    def load_payment_data(self):
        self.db.connect()
        try:
            r = self.db.cursor.execute("SELECT invoice_id, payment_date, amount, payment_method FROM payments WHERE payment_id=?", (self.payment_id,)).fetchone()
            if r:
                # Fatura Seç
                idx = self.cmb_invoice.findData(r[0]) 
                # Not: findData varsayılan olarak tüm nesneyi karşılaştırır, ID'yi eşleştirmemiz gerekir. 
                # QComboBox findData, tam eşleşme olmadığı sürece sözlüklerle esnek değildir.
                # Bulmak için döngü
                for i in range(self.cmb_invoice.count()):
                    d = self.cmb_invoice.itemData(i)
                    if d and d['id'] == r[0]:
                        self.cmb_invoice.setCurrentIndex(i)
                        break
                        
                self.cmb_invoice.setEnabled(False) # Ödeme düzenlerken fatura değiştirmeyi devre dışı bırak
                
                self.inp_date.setDate(QDate.fromString(r[1], "yyyy-MM-dd"))
                self.spn_amount.setValue(r[2])
                self.cmb_method.setCurrentText(r[3])
        finally:
            self.db.disconnect()

    def on_invoice_change(self):
        data = self.cmb_invoice.currentData()
        if data and "remaining" in data:
            self.spn_amount.setValue(data["remaining"])

    def save(self):
        data = self.cmb_invoice.currentData()
        if not data: return
        
        inv_id = data["id"]
        amount = self.spn_amount.value()
        
        if amount <= 0:
            CustomDialogs.warning(self, "Ödeme tutarı 0'dan büyük olmalıdır.")
            return
        
        self.db.connect()
        try:
            # Öncelikle, fazla ödemeyi doğrula
            total = self.db.cursor.execute("SELECT total_amount FROM invoices WHERE invoice_id=?", (inv_id,)).fetchone()[0]
            
            # Mevcut ödemeleri hesapla (düzenliyorsak mevcut ödemeyi hariç tut)
            if self.payment_id:
                existing_paid = self.db.cursor.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id=? AND payment_id!=?", 
                    (inv_id, self.payment_id)
                ).fetchone()[0]
            else:
                existing_paid = self.db.cursor.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id=?", 
                    (inv_id,)
                ).fetchone()[0]
            
            new_total_paid = existing_paid + amount
            
            # Fazla ödeme olup olmadığını kontrol et (Float hassasiyet düzeltmesi)
            if round(new_total_paid, 2) > round(total, 2):
                remaining = total - existing_paid
                CustomDialogs.warning(
                    self, 
                    f"Ödeme tutarı fatura toplamını aşamaz!\n\n"
                    f"Fatura Toplamı: {total:,.2f} TL\n"
                    f"Mevcut Ödeme: {existing_paid:,.2f} TL\n"
                    f"Kalan Tutar: {remaining:,.2f} TL\n\n"
                    f"Girilen tutar ({amount:,.2f} TL) kalan tutardan fazla."
                )
                return
            
            # Kaydetme ile devam et
            if self.payment_id:
                self.db.cursor.execute("UPDATE payments SET payment_date=?, amount=?, payment_method=? WHERE payment_id=?",
                                       (self.inp_date.text(), amount, self.cmb_method.currentText(), self.payment_id))
            else:
                self.db.cursor.execute("INSERT INTO payments (invoice_id, payment_date, amount, payment_method) VALUES (?, ?, ?, ?)",
                                   (inv_id, self.inp_date.text(), amount, self.cmb_method.currentText()))
            
            # Fatura Durum Mantığını Güncelle (Yeniden Hesapla)
            total = self.db.cursor.execute("SELECT total_amount FROM invoices WHERE invoice_id=?", (inv_id,)).fetchone()[0]
            paid_sum = self.db.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id=?", (inv_id,)).fetchone()[0]
            
            new_status = 2 # Bekliyor
            if round(paid_sum, 2) >= round(total, 2):
                new_status = 1 # Ödendi
            elif round(paid_sum, 2) > 0:
                new_status = 3 # Kısmi
            
            self.db.cursor.execute("UPDATE invoices SET status_id=? WHERE invoice_id=?", (new_status, inv_id))
            
            self.db.conn.commit()
            
            action = "güncellendi" if self.payment_id else "alındı"
            self.logger.info(f"Ödeme {action}. Kayıt ID: {inv_id}, Tutar: {amount}")
            
            CustomDialogs.info(self, "Ödeme kaydedildi.")
            self.accept()
        except Exception as e:
            self.logger.error(f"Ödeme kaydedilirken hata: {e}")
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()
