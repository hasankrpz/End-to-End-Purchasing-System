from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QDialog, QFormLayout, 
                             QMessageBox, QAbstractItemView, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper
from utils.text_utils import turkish_lower

class PageTedarikciDetay(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logger = Logger()
        self.init_ui()

    def showEvent(self, event):
        """Verileri veritabanından yeniden yükle (Yenile)"""
        self.load_data()
        super().showEvent(event)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # ÜST ÇUBUK
        top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Tedarikçi Listesi ve Yönetimi")
        self.lbl_title.setObjectName("PageTitle")
        top_bar.addWidget(self.lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Firma Ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search_input)

        top_bar.addStretch()

        self.btn_add = QPushButton("Yeni Tedarikçi")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_popup)
        top_bar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.clicked.connect(self.open_edit_popup)
        top_bar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Sil")
        self.btn_delete.clicked.connect(self.delete_supplier)
        top_bar.addWidget(self.btn_delete)

        self.layout.addLayout(top_bar)

        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Firma Adı", "İletişim Kişisi", "E-Mail", "IBAN", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)
        
        self.load_data()

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E5E7EB;")
            self.search_input.setStyleSheet("padding: 8px; border: 1px solid #4B5563; border-radius: 6px; background-color: #1F2937; color: #F9FAFB;")
            
            self.btn_add.setStyleSheet("""
                QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} 
                QPushButton:hover { background-color: #047857; }
            """)
            self.btn_edit.setStyleSheet("""
                QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} 
                QPushButton:hover { background-color: #78350F; }
            """)
            self.btn_delete.setStyleSheet("""
                QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} 
                QPushButton:hover { background-color: #7F1D1D; }
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
            
            self.btn_add.setStyleSheet("QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }")
            self.btn_delete.setStyleSheet("QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)

        if is_dark:
             pass

    def load_data(self):
        self.table.setSortingEnabled(False)
        search_text = self.search_input.text()
        search_lower = turkish_lower(search_text)
        
        query = """
            SELECT s.supplier_id, s.company_name, s.contact_name, s.email, s.iban, ss.status_name, s.black_list 
            FROM suppliers s 
            LEFT JOIN supplier_statuses ss ON s.status_id = ss.status_id 
            WHERE 1=1
        """
        params = []
        
        query += " ORDER BY s.supplier_id ASC"

        self.db.connect()
        try:
            self.db.cursor.execute(query, params)
            rows = self.db.cursor.fetchall()
            
            # Özel Filtre Başlığını Ayarla Search
            filtered_rows = []
            if search_text:
                for row in rows:
                    # Çoğaltmayı kontrol etsible columns for match
                    # row: 0=id, 1=name, 2=contact, 3=email, 4=iban, 5=status, 6=blacklist
                    # Visible: ID, Name, Contact, Email, IBAN, Status
                    # We usually search in Name, Contact, Email, IBAN.
                    row_content = f"{row[0]} {row[1]} {row[2]} {row[3]} {row[4]}".replace("None", "")
                    if search_lower in turkish_lower(row_content):
                        filtered_rows.append(row)
            else:
                filtered_rows = rows

            self.table.setRowCount(0)
            
            # Vurgula Colors
            is_dark = getattr(self, 'is_dark', False)
            if is_dark:
                 highlight_bg = QColor("#92400E") # Amber-800
                 highlight_fg = QColor("#FEF3C7")      # Amber-100
            else:
                 highlight_bg = QColor("#FEF08A") # Yellow-200
                 highlight_fg = QColor("#000000")      # Black

            for r_idx, row in enumerate(filtered_rows):
                self.table.insertRow(r_idx)
                
                # row structure: 0=id, 1=name, 2=contact, 3=email, 4=iban, 5=status_name, 6=black_list
                status_name = row[5]
                is_blacklisted = row[6] == 1
                
                # Güncellermine Row Base Color
                row_bg = None
                row_fg = None
                
                if is_blacklisted:
                    row_bg = QColor("#fee2e2") # Light Red
                    row_fg = QColor("#b91c1c") # Dark Red
                elif status_name == 'Pasif':
                    row_bg = QColor("#E5E7EB") # Gray-200
                    row_fg = QColor("#374151") # Gray-700
                
                for c_idx in range(6): 
                    val = row[c_idx]
                    
                    if c_idx == 5:
                        # Status Column Display
                        if is_blacklisted:
                            display = val if val == "Kara Liste" else f"Kara Liste ({val})"
                        else:
                            display = str(val if val else "")
                        item = QTableWidgetItem(display)
                    else:
                        item = QTableWidgetItem(str(val) if val is not None else "")
                    
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Varsa filtreleri yeniden uygula(Highlight if match, else Base)
                    is_match = False
                    if search_text:
                         cell_text_lower = turkish_lower(item.text())
                         if search_lower in cell_text_lower:
                             is_match = True
                    
                    if is_match:
                        item.setBackground(highlight_bg)
                        item.setForeground(highlight_fg)
                    else:
                        if row_bg: item.setBackground(row_bg)
                        if row_fg: item.setForeground(row_fg)
                        
                    self.table.setItem(r_idx, c_idx, item)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.db.disconnect()

    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        dialog = SupplierPopup(self, is_dark=is_dark)
        if dialog.exec():
            self.load_data()

    def open_edit_popup(self):
        row = self.table.currentRow()
        if row < 0: return CustomDialogs.warning(self, "Lütfen düzenlenecek tedarikçi seçin.")
        
        rec_id = self.table.item(row, 0).text()
        is_dark = getattr(self, 'is_dark', False)
        dialog = SupplierPopup(self, rec_id, is_dark=is_dark)
        if dialog.exec():
            self.load_data()

    def delete_supplier(self):
        row = self.table.currentRow()
        if row < 0: return CustomDialogs.warning(self, "Silinecek tedarikçi seçin.")
        
        sid = self.table.item(row, 0).text()
        if CustomDialogs.question(self, "Silmek istediğinize emin misiniz?", "Onay"):
            self.db.connect()
            try:
                # Önce bağımlı kayıtları kontrol et (Foreign Key Hatasını önlemek için)
                cnt_offers = self.db.cursor.execute("SELECT COUNT(*) FROM offers WHERE supplier_id=?", (sid,)).fetchone()[0]
                if cnt_offers > 0:
                    CustomDialogs.warning(self, f"Bu tedarikçiye ait {cnt_offers} adet teklif kaydı bulunuyor. Önce ilgili teklifleri silmelisiniz.", "İşlem Engellendi")
                    return

                cnt_invoices = self.db.cursor.execute("SELECT COUNT(*) FROM invoices WHERE supplier_id=?", (sid,)).fetchone()[0]
                if cnt_invoices > 0:
                    CustomDialogs.warning(self, f"Bu tedarikçiye ait {cnt_invoices} adet fatura kaydı bulunuyor. Önce ilgili faturaları silmelisiniz.", "İşlem Engellendi")
                    return

                self.db.cursor.execute("DELETE FROM suppliers WHERE supplier_id=?", (sid,))
                self.db.conn.commit()
                self.logger.info(f"Tedarikçi silindi. ID: {sid}")
                CustomDialogs.info(self, "Tedarikçi silindi.")
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, str(e))
                self.logger.error(f"Tedarikçi silme hatası: {e}")
            finally:
                self.db.disconnect()

class SupplierPopup(QDialog):
    def __init__(self, parent=None, supplier_id=None, is_dark=False):
        super().__init__(parent)
        
        # Apply Theme
        ThemeHelper.apply_popup_theme(self, is_dark)
        
        self.setWindowTitle("Tedarikçi İşlemleri")
        self.setFixedSize(350, 300)
        self.supplier_id = supplier_id
        self.db = DatabaseManager()
        
        layout = QFormLayout(self)
        self.inp_name = QLineEdit()
        self.inp_contact = QLineEdit()
        self.inp_email = QLineEdit()
        self.inp_iban = QLineEdit()
        self.cmb_status = QComboBox() 
        self.check_blacklist = QCheckBox("Kara Listeye Al")

        # ComboBox Doldur (Sadece Aktif/Pasif)
        # self.db.load_combobox_data(self.cmb_status, "supplier_statuses", "status_id", "status_name")
        # Custom load to filter or ensure order if needed, but load_combobox_data loads all. 
        # User requested: "Sadece Aktif ve Pasif seçilsin". 
        # Assuming other statuses might exist? Or maybe just 'Aktif' and 'Pasif' exist.
        # Let's use load_combobox_data with condition if possible or manual load.
        self.load_custom_statuses()
        
        layout.addRow("Firma Adı:", self.inp_name)
        layout.addRow("İletişim Kişisi:", self.inp_contact)
        layout.addRow("E-Mail:", self.inp_email)
        layout.addRow("IBAN:", self.inp_iban)
        layout.addRow("Durum:", self.cmb_status)
        layout.addRow("Kara Liste:", self.check_blacklist)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        if self.supplier_id:
            self.load_details()

    def load_details(self):
        self.db.connect()
        try:
            r = self.db.cursor.execute("SELECT company_name, contact_name, email, iban, black_list, status_id FROM suppliers WHERE supplier_id=?", (self.supplier_id,)).fetchone()
            if r:
                self.inp_name.setText(r[0])
                self.inp_contact.setText(r[1])
                self.inp_email.setText(r[2])
                self.inp_iban.setText(r[3])
                self.check_blacklist.setChecked(r[4] == 1)
                
                # Set ComboBox Selection
                idx = self.cmb_status.findData(r[5])
                if idx >= 0:
                    self.cmb_status.setCurrentIndex(idx)
        finally:
            self.db.disconnect()

    def load_custom_statuses(self):
        """Sadece Aktif ve Pasif seçeneklerini yükle"""
        self.cmb_status.clear()
        self.db.connect()
        try:
            # We explicitly want 'Aktif' and 'Pasif'.
            query = "SELECT status_id, status_name FROM supplier_statuses WHERE status_name IN ('Aktif', 'Pasif')"
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            for r in rows:
                self.cmb_status.addItem(r[1], r[0])
        except Exception as e:
            print(f"Status Load Error: {e}")
        finally:
            self.db.disconnect()

    def save(self):
        try:
            name = self.inp_name.text()
            contact = self.inp_contact.text()
            email = self.inp_email.text()
            iban = self.inp_iban.text()
            is_blacklisted = 1 if self.check_blacklist.isChecked() else 0
            
            # Get Selected Status ID
            status_id = self.cmb_status.currentData()
            # Durum aktifse silmeyi önle? (İsteğe bağlı, belki sadece uyarı)
            # Alternatif olarak, bağımlılığı kontrol et (siparişler, teklifler)elf.db.connect()
            if status_id is None:
                 status_id = 1 

            self.db.connect()
            if self.supplier_id:
                # UPDATE
                self.db.cursor.execute("UPDATE suppliers SET company_name=?, contact_name=?, email=?, status_id=?, iban=?, black_list=? WHERE supplier_id=?", 
                                       (name, contact, email, status_id, iban, is_blacklisted, self.supplier_id))
                Logger().info(f"Tedarikçi güncellendi. ID: {self.supplier_id}, Kara Liste: {is_blacklisted}")
            else:
                # INSERT
                self.db.cursor.execute("INSERT INTO suppliers (company_name, contact_name, email, status_id, iban, black_list) VALUES (?, ?, ?, ?, ?, ?)",
                                       (name, contact, email, status_id, iban, is_blacklisted))
                Logger().info(f"Yeni tedarikçi eklendi. Firma: {name}, Kara Liste: {is_blacklisted}")

            self.db.conn.commit()
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
            Logger().error(f"Tedarikçi kaydetme hatası: {e}")
        finally:
            self.db.disconnect()
