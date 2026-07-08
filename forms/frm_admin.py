from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QHeaderView, QAbstractItemView,
                             QMessageBox, QDialog, QFormLayout, QComboBox, QCheckBox, QTextEdit, QDoubleSpinBox, QAbstractSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper

# =========================================================
# GENERIC LOOKUP EDITOR (Tanımlamalar İçin)
# =========================================================
class LookupEditor(QWidget):
    """
    Basit (ID, Ad) yapısındaki tabloları yönetmek için.
    Örn: Kategoriler, Birimler, Departmanlar, Roller, Para Birimleri, Durumlar
    """
    def __init__(self, table_name, id_col, name_col, display_name):
        super().__init__()
        self.table_name = table_name
        self.id_col = id_col
        self.name_col = name_col
        self.display_name = display_name
        self.db = DatabaseManager()
        self.logger = Logger()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        top_bar = QHBoxLayout()
        self.lbl_header = QLabel(f"{self.display_name} Yönetimi")
        self.lbl_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_bar.addWidget(self.lbl_header)
        
        self.inp_name = QLineEdit()
        if self.table_name == 'currencies':
            self.inp_name.setPlaceholderText("Kod - Sembol - Ad (Örn: USD - $ - Dolar)")
        else:
            self.inp_name.setPlaceholderText(f"Yeni {self.display_name} Adı...")
        top_bar.addWidget(self.inp_name)
        
        self.btn_add = QPushButton("Ekle")
        self.btn_add.clicked.connect(self.add_item)
        top_bar.addWidget(self.btn_add)
        
        layout.addLayout(top_bar)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Adı"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # İşlemler
        action_bar = QHBoxLayout()
        
        self.btn_edit = QPushButton("Seçili Olanı Düzenle")
        self.btn_edit.clicked.connect(self.edit_item)
        action_bar.addWidget(self.btn_edit)

        self.btn_del = QPushButton("Seçili Olanı Sil")
        self.btn_del.clicked.connect(self.delete_item)
        action_bar.addWidget(self.btn_del)
        layout.addLayout(action_bar)
        
        self.load_data()

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.lbl_header.setStyleSheet("color: #E5E7EB; font-size: 16px; font-weight: bold;")
            self.inp_name.setStyleSheet("padding: 8px; border: 1px solid #4B5563; border-radius: 6px; background-color: #1F2937; color: #F9FAFB;")
            self.btn_add.setStyleSheet("QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} QPushButton:hover { background-color: #047857; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} QPushButton:hover { background-color: #78350F; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} QPushButton:hover { background-color: #7F1D1D; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #111827; color: #E5E7EB; gridline-color: #374151; border: none; alternate-background-color: #1F2937; }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section { background-color: #1F2937; color: #9CA3AF; border: none; border-bottom: 2px solid #374151; padding: 4px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
            self.table.setAlternatingRowColors(True)
        else:
            self.lbl_header.setStyleSheet("color: #111827; font-size: 16px; font-weight: bold;")
            self.inp_name.setStyleSheet("padding: 8px; border: 1px solid #D1D5DB; border-radius: 6px; background-color: #FFFFFF; color: #111827;")
            self.btn_add.setStyleSheet("QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)

    def load_data(self):
        self.table.setRowCount(0)
        self.db.connect()
        try:
            query = f"SELECT {self.id_col}, {self.name_col} FROM {self.table_name}"
            if self.table_name == 'currencies':
                 query = f"SELECT {self.id_col}, code || ' - ' || name FROM {self.table_name}"

            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            
            for r_idx, row in enumerate(rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        except Exception as e:
            print(f"Lookup Load Error ({self.table_name}): {e}")
        finally:
            self.db.disconnect()

    def add_item(self):
        val = self.inp_name.text().strip()
        if not val: return
        
        self.db.connect()
        try:
            if self.table_name == 'currencies':
                # Formatı ayrıştır: Kod - Sembol - Ad
                parts = [p.strip() for p in val.split('-')]
                if len(parts) >= 3:
                     code = parts[0].upper()
                     symbol = parts[1]
                     name = parts[2]
                elif len(parts) == 2:
                     code = parts[0].upper()
                     symbol = parts[0] # Kodu sembol olarak varsay
                     name = parts[1]
                else:
                     code = parts[0].upper()
                     symbol = ""
                     name = parts[0]

                self.db.cursor.execute("INSERT INTO currencies (code, symbol, name) VALUES (?, ?, ?)", (code, symbol, name))
            
            elif self.table_name == 'units':
                self.db.cursor.execute(f"INSERT INTO {self.table_name} (unit_code, unit_name) VALUES (?, ?)", (val[:3].upper(), val))
            elif self.table_name == 'roles':
                self.db.cursor.execute(f"INSERT INTO {self.table_name} (title) VALUES (?)", (val,))
            else:
                self.db.cursor.execute(f"INSERT INTO {self.table_name} ({self.name_col}) VALUES (?)", (val,))
                
            self.db.conn.commit()
            self.inp_name.clear()
            self.load_data()
            self.logger.info(f"{self.display_name} eklendi: {val}")
        except Exception as e:
            self.db.conn.rollback()
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()

    def edit_item(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek kaydı seçin.")
            return

        id_val = self.table.item(row, 0).text()
        current_name = self.table.item(row, 1).text()
        
        # Use QInputDialog
        from PyQt6.QtWidgets import QInputDialog
        new_val, ok = QInputDialog.getText(self, "Düzenle", f"Yeni {self.display_name} Adı:", text=current_name)
        
        if ok and new_val.strip():
            self.db.connect()
            try:
                if self.table_name == 'currencies':
                     # Basit ayrıştırma tam desteklenmiyor, tek satırda karmaşık düzenleme
                     # ama kullanıcının "USD - $ - Dolar" şeklinde düzenlediğini varsayalım
                     # Tekrar ekleme mantığını kullan veya doğrudan adı güncelle?
                     # En iyisi: Tekrar ayır
                     val = new_val.strip()
                     parts = [p.strip() for p in val.split('-')]
                     if len(parts) >= 3:
                         code, symbol, name = parts[0].upper(), parts[1], parts[2]
                     elif len(parts) == 2:
                         code, symbol, name = parts[0].upper(), parts[0], parts[1]
                     else:
                         code, symbol, name = parts[0].upper(), "", parts[0]
                         
                     self.db.cursor.execute("UPDATE currencies SET code=?, symbol=?, name=? WHERE currency_id=?", 
                                          (code, symbol, name, id_val))
                                          
                elif self.table_name == 'units':
                    self.db.cursor.execute(f"UPDATE {self.table_name} SET unit_code=?, unit_name=? WHERE {self.id_col}=?", 
                                         (new_val[:3].upper(), new_val, id_val))
                elif self.table_name == 'roles':
                     self.db.cursor.execute(f"UPDATE {self.table_name} SET title=? WHERE {self.id_col}=?", (new_val, id_val))
                else:
                    self.db.cursor.execute(f"UPDATE {self.table_name} SET {self.name_col}=? WHERE {self.id_col}=?", (new_val.strip(), id_val))
                    
                self.db.conn.commit()
                self.load_data()
                self.logger.info(f"{self.display_name} güncellendi: {current_name} -> {new_val}")
                
            except Exception as e:
                CustomDialogs.error(self, str(e))
            finally:
                self.db.disconnect()

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0: return
        
        id_val = int(self.table.item(row, 0).text())
        name_val = self.table.item(row, 1).text()
        
        if CustomDialogs.question(self, f"'{name_val}' kaydını silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                # Veritabanı (Backend) Kontrolleri
                check_map = {
                    'departments': [('users', 'department_id', "Bu departmana bağlı kullanıcılar var.")],
                    'units': [('items', 'unit_id', "Bu birimi kullanan ürünler var.")],
                    'categories': [('items', 'category_id', "Bu kategoriye bağlı ürünler var.")],
                    'roles': [('users', 'role_id', "Bu role sahip kullanıcılar var.")]
                }
                
                if self.table_name in check_map:
                    for ref_table, ref_col, msg in check_map[self.table_name]:
                        cnt = self.db.cursor.execute(f"SELECT COUNT(*) FROM {ref_table} WHERE {ref_col}=?", (id_val,)).fetchone()[0]
                        if cnt > 0:
                            CustomDialogs.warning(self, f"{msg} ({cnt} Kayıt)\n\nSilme işlemi engellendi.", "Silinemez")
                            return

                self.db.cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_col}=?", (id_val,))
                
                self.db.conn.commit()
                self.load_data()
                self.logger.info(f"{self.display_name} silindi: {id_val}")
                
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, f"Silinemedi (Kullanılıyor olabilir): {e}")
            finally:
                self.db.disconnect()


# =========================================================
# ÜRÜN EDİTÖRÜ (Ürünler İçin)
# =========================================================
class ItemEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        top_bar = QHBoxLayout()
        self.lbl_header = QLabel("Ürün Yönetimi")
        self.lbl_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_bar.addWidget(self.lbl_header)
        top_bar.addStretch()
        
        self.btn_add = QPushButton("Yeni Ürün Ekle")
        self.btn_add.clicked.connect(self.open_add_popup)
        top_bar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.clicked.connect(self.open_edit_popup)
        top_bar.addWidget(self.btn_edit)
        
        self.btn_del = QPushButton("Ürünü ve İlişkili Kayıtları Sil")
        self.btn_del.clicked.connect(self.delete_item)
        top_bar.addWidget(self.btn_del)
        
        layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Kategori", "Birim"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        self.load_data()

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.lbl_header.setStyleSheet("color: #E5E7EB; font-size: 16px; font-weight: bold;")
            self.btn_add.setStyleSheet("QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} QPushButton:hover { background-color: #047857; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} QPushButton:hover { background-color: #78350F; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} QPushButton:hover { background-color: #7F1D1D; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #111827; color: #E5E7EB; gridline-color: #374151; border: none; alternate-background-color: #1F2937; }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section { background-color: #1F2937; color: #9CA3AF; border: none; border-bottom: 2px solid #374151; padding: 4px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
            self.table.setAlternatingRowColors(True)
        else:
            self.lbl_header.setStyleSheet("color: #111827; font-size: 16px; font-weight: bold;")
            self.btn_add.setStyleSheet("QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)

    def load_data(self):
        self.table.setRowCount(0)
        self.db.connect()
        try:
            query = """
                SELECT i.item_id, i.item_name, c.category_name, u.unit_name
                FROM items i
                LEFT JOIN categories c ON i.category_id = c.category_id
                LEFT JOIN units u ON i.unit_id = u.unit_id
            """
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            for r_idx, row in enumerate(rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        finally:
            self.db.disconnect()

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0: return
        
        id_val = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        
        if CustomDialogs.question(self, f"'{name}' ürününü ve ürünle ilişkili verileri silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                # Veritabanı Kontrolü
                cnt = self.db.cursor.execute("SELECT COUNT(*) FROM purchase_requests WHERE item_id=?", (id_val,)).fetchone()[0]
                if cnt > 0:
                    CustomDialogs.warning(self, f"Bu ürüne ait {cnt} adet satın alma talebi mevcut.\n\nVeri bütünlüğü için önce talepleri silmelisiniz.", "Silinemez")
                    return

                # 1. DELETE
                self.db.cursor.execute("DELETE FROM items WHERE item_id=?", (id_val,))
                
                self.db.conn.commit()
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        d = ItemPopup(self, is_dark=is_dark)
        if d.exec(): self.load_data()

    def open_edit_popup(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek ürünü seçin.")
            return

        item_id = self.table.item(row, 0).text()
        is_dark = getattr(self, 'is_dark', False)
        d = ItemPopup(self, item_id=item_id, is_dark=is_dark)
        if d.exec(): self.load_data()

class ItemPopup(QDialog):
    def __init__(self, parent=None, item_id=None, is_dark=False):
        super().__init__(parent)
        
        self.item_id = item_id
        self.setWindowTitle("Ürün Düzenle" if item_id else "Ürün Ekle")
        self.db = DatabaseManager()
        self.logger = Logger()
        layout = QFormLayout(self)
        
        self.inp_name = QLineEdit()
        self.cmb_cat = QComboBox()
        self.cmb_unit = QComboBox()
        
        self.db.load_combobox_data(self.cmb_cat, "categories", "category_id", "category_name")
        self.db.load_combobox_data(self.cmb_unit, "units", "unit_id", "unit_name")
        
        layout.addRow("Ürün Adı:", self.inp_name)
        layout.addRow("Kategori:", self.cmb_cat)
        layout.addRow("Birim:", self.cmb_unit)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        if self.item_id:
            self.load_details()

        # Temayı Uygula (Başlatma Sonu)
        ThemeHelper.apply_popup_theme(self, is_dark)

    def load_details(self):
        self.db.connect()
        try:
            r = self.db.cursor.execute("SELECT item_name, category_id, unit_id FROM items WHERE item_id=?", (self.item_id,)).fetchone()
            if r:
                self.inp_name.setText(r[0])
                idx = self.cmb_cat.findData(r[1])
                if idx >= 0: self.cmb_cat.setCurrentIndex(idx)
                idx = self.cmb_unit.findData(r[2])
                if idx >= 0: self.cmb_unit.setCurrentIndex(idx)
        finally:
            self.db.disconnect()

    def save(self):
        try:
            self.db.connect()
            if self.item_id:
                # UPDATE
                self.db.cursor.execute("""
                    UPDATE items SET item_name=?, category_id=?, unit_id=?
                    WHERE item_id=?
                """, (self.inp_name.text(), self.cmb_cat.currentData(), self.cmb_unit.currentData(), self.item_id))
            else:
                # INSERT
                self.db.cursor.execute("""
                    INSERT INTO items (item_name, category_id, unit_id)
                    VALUES (?, ?, ?)
                """, (self.inp_name.text(), self.cmb_cat.currentData(), self.cmb_unit.currentData()))
            
            self.db.conn.commit()
            action = "güncellendi" if self.item_id else "eklendi"
            self.logger.info(f"Ürün {action}: {self.inp_name.text()}")
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()

# =========================================================
# KULLANICI YÖNETİMİ (Kullanıcılar İçin)
# =========================================================
class UserEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Araçlar
        tb = QHBoxLayout()
        self.btn_add = QPushButton("Yeni Kullanıcı")
        self.btn_add.clicked.connect(self.open_add_popup)
        tb.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Kullanıcı Düzenle")
        self.btn_edit.clicked.connect(self.open_edit_popup)
        tb.addWidget(self.btn_edit)
        
        self.btn_del = QPushButton("Kullanıcı Sil")
        self.btn_del.clicked.connect(self.delete_user)
        tb.addWidget(self.btn_del)
        
        tb.addStretch()
        layout.addLayout(tb)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Ad Soyad", "E-Mail", "Rol", "Departman", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        self.load_data()
    
    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.btn_add.setStyleSheet("QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} QPushButton:hover { background-color: #047857; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} QPushButton:hover { background-color: #78350F; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} QPushButton:hover { background-color: #7F1D1D; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #111827; color: #E5E7EB; gridline-color: #374151; border: none; alternate-background-color: #1F2937; }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section { background-color: #1F2937; color: #9CA3AF; border: none; border-bottom: 2px solid #374151; padding: 4px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
            self.table.setAlternatingRowColors(True)
        else:
            self.btn_add.setStyleSheet("QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }")
            self.btn_edit.setStyleSheet("QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }")
            self.btn_del.setStyleSheet("QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)
            self.table.setAlternatingRowColors(True)

    def load_data(self):
        self.table.setRowCount(0)
        self.db.connect()
        try:
            query = """
                SELECT u.user_id, u.first_name || ' ' || COALESCE(u.last_name, ''), 
                       u.email, r.title, d.department_name, u.is_active
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
                LEFT JOIN departments d ON u.department_id = d.department_id
            """
            self.db.cursor.execute(query)
            for r_idx, row in enumerate(self.db.cursor.fetchall()):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    if c_idx == 5:
                        val = "Aktif" if val == 1 else "Pasif"
                    self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        finally:
            self.db.disconnect()
            
    def delete_user(self):
        row = self.table.currentRow()
        if row < 0: return

        id_val = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        
        if CustomDialogs.question(self, f"'{name}' kullanıcısını silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                # Veritabanı Kontrolü
                cnt = self.db.cursor.execute("SELECT COUNT(*) FROM purchase_requests WHERE requester_user_id=?", (id_val,)).fetchone()[0]
                if cnt > 0:
                    CustomDialogs.warning(self, f"Bu kullanıcıya ait {cnt} adet satın alma talebi mevcut.\n\nKullanıcıyı silmeden önce taleplerini silmeli veya başka kullanıcıya aktarmalısınız.", "Silinemez")
                    return

                # 1. DELETE
                self.db.cursor.execute("DELETE FROM users WHERE user_id=?", (id_val,))
                
                self.db.conn.commit()
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, f"Hata: {e}")
            finally:
                self.db.disconnect()

    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        d = UserPopup(self, is_dark=is_dark)
        if d.exec(): self.load_data()

    def open_edit_popup(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek kullanıcıyı seçin.")
            return

        user_id = self.table.item(row, 0).text()
        is_dark = getattr(self, 'is_dark', False)
        d = UserPopup(self, is_dark=is_dark, user_id=user_id)
        if d.exec(): self.load_data()

class UserPopup(QDialog):
    def __init__(self, parent=None, is_dark=False, user_id=None):
        super().__init__(parent)
        
        self.user_id = user_id
        self.setWindowTitle("Kullanıcı Düzenle" if user_id else "Kullanıcı Ekle")
        self.db = DatabaseManager()
        self.logger = Logger()
        layout = QFormLayout(self)
        
        self.inp_fname = QLineEdit()
        self.inp_lname = QLineEdit()
        self.inp_email = QLineEdit()
        self.inp_pass = QLineEdit()
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setPlaceholderText("Değiştirmek istemiyorsanız boş bırakın" if user_id else "")
        
        self.cmb_role = QComboBox()
        self.cmb_dept = QComboBox()
        self.chk_active = QCheckBox("Aktif")
        self.chk_active.setChecked(True)
        
        # Load combos
        self.db.load_combobox_data(self.cmb_role, "roles", "role_id", "title")
        self.db.load_combobox_data(self.cmb_dept, "departments", "department_id", "department_name")
        
        layout.addRow("Ad:", self.inp_fname)
        layout.addRow("Soyad:", self.inp_lname)
        layout.addRow("E-Mail:", self.inp_email)
        layout.addRow("Şifre:", self.inp_pass)
        layout.addRow("Rol:", self.cmb_role)
        layout.addRow("Departman:", self.cmb_dept)
        layout.addRow("", self.chk_active)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        if self.user_id:
            self.load_details()

        # Apply Theme (End of Init)
        ThemeHelper.apply_popup_theme(self, is_dark)

    def load_details(self):
        self.db.connect()
        try:
            row = self.db.cursor.execute("""
                SELECT first_name, last_name, email, role_id, department_id, is_active 
                FROM users WHERE user_id=?
            """, (self.user_id,)).fetchone()
            
            if row:
                self.inp_fname.setText(row[0])
                self.inp_lname.setText(row[1])
                self.inp_email.setText(row[2])
                
                # Role Combo
                idx = self.cmb_role.findData(row[3])
                if idx >= 0: self.cmb_role.setCurrentIndex(idx)
                
                # Dept Combo
                idx = self.cmb_dept.findData(row[4])
                if idx >= 0: self.cmb_dept.setCurrentIndex(idx)
                
                self.chk_active.setChecked(bool(row[5]))
                
        finally:
            self.db.disconnect()

    def save(self):
        try:
            self.db.connect()
            
            if self.user_id:
                # UPDATE
                if self.inp_pass.text().strip():
                    # Şifre ile güncelle
                    self.db.cursor.execute("""
                        UPDATE users SET first_name=?, last_name=?, email=?, password_hash=?, 
                        role_id=?, department_id=?, is_active=?
                        WHERE user_id=?
                    """, (self.inp_fname.text(), self.inp_lname.text(), self.inp_email.text(), 
                          self.inp_pass.text(), self.cmb_role.currentData(), self.cmb_dept.currentData(), 
                          1 if self.chk_active.isChecked() else 0, self.user_id))
                else:
                    # Şifresiz güncelle
                    self.db.cursor.execute("""
                        UPDATE users SET first_name=?, last_name=?, email=?, 
                        role_id=?, department_id=?, is_active=?
                        WHERE user_id=?
                    """, (self.inp_fname.text(), self.inp_lname.text(), self.inp_email.text(), 
                          self.cmb_role.currentData(), self.cmb_dept.currentData(), 
                          1 if self.chk_active.isChecked() else 0, self.user_id))
            else:
                # INSERT
                self.db.cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, password_hash, role_id, department_id, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.inp_fname.text(), self.inp_lname.text(), self.inp_email.text(), 
                      self.inp_pass.text(), self.cmb_role.currentData(), self.cmb_dept.currentData(), 
                      1 if self.chk_active.isChecked() else 0))
            
            self.db.conn.commit()
            action = "güncellendi" if self.user_id else "eklendi"
            self.logger.info(f"Kullanıcı {action}: {self.inp_email.text()}")
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()


# =========================================================
# ANA YÖNETİCİ SAYFASI
# =========================================================

# =========================================================
# DEPARTMENT EDITOR (Bütçeli)
# =========================================================





    def delete_item(self):
        row = self.table.currentRow()
        if row < 0: return
        
        id_val = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        
        if CustomDialogs.question(self, f"'{name}' departmanını silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                self.db.cursor.execute("DELETE FROM departments WHERE department_id=?", (id_val,))
                self.db.conn.commit()
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, f"Silinemedi: {e}")
            finally:
                self.db.disconnect()



# BÜTÇE EDİTÖRÜ (Standartlaştırılmış)
# =========================================================
class BudgetEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.lookups_loaded = False
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # 1. ÜST ÇUBUK
        top_bar = QHBoxLayout()
        
        self.lbl_title = QLabel("Yıllık Bütçe Yönetimi")
        self.lbl_title.setObjectName("PageTitle")
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;") 
        top_bar.addWidget(self.lbl_title)
        
        top_bar.addStretch()
        
        # Arama/Filtre Alanı
        self.cmb_filter_dept = QComboBox()
        self.cmb_filter_dept.setFixedWidth(180)
        self.cmb_filter_dept.addItem("Tüm Departmanlar", None)
        self.cmb_filter_dept.currentIndexChanged.connect(self.load_data)
        
        self.spn_filter_year = QDoubleSpinBox()
        self.spn_filter_year.setDecimals(0)
        self.spn_filter_year.setRange(2020, 2030)
        self.spn_filter_year.setValue(2025)
        self.spn_filter_year.setPrefix("Yıl: ")
        self.spn_filter_year.setFixedWidth(100)
        self.spn_filter_year.valueChanged.connect(self.load_data)

        self.btn_reset = QPushButton("Sıfırla")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)

        top_bar.addWidget(QLabel("Filtre:"))
        top_bar.addWidget(self.cmb_filter_dept)
        top_bar.addWidget(self.spn_filter_year)
        top_bar.addWidget(self.btn_reset)

        self.layout.addLayout(top_bar)
        
        # 2. İŞLEM ÇUBUĞU
        action_bar = QHBoxLayout()
        
        self.btn_add = QPushButton("Yeni Yıllık Bütçe Ekle")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_popup)
        action_bar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.clicked.connect(self.open_edit_popup)
        action_bar.addWidget(self.btn_edit)
        
        self.btn_del = QPushButton("Sil")
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.clicked.connect(self.delete_item)
        action_bar.addWidget(self.btn_del)
        
        action_bar.addStretch()
        self.layout.addLayout(action_bar)
        
        # 3. TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(3) # Dept, Tutar, ID
        self.table.setHorizontalHeaderLabels(["Departman", "Yıllık Bütçe Tutarı", "ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.hideColumn(2) # ID gizle
        self.layout.addWidget(self.table)
        
        # Verileri Başlat
        self.load_departments() # Açılır kutuları yükle
        self.load_data()

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        
        # Ortak Stiller
        button_style_green = "QPushButton { background-color: #10B981; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #059669; }"
        button_style_orange = "QPushButton { background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #D97706; }"
        button_style_red = "QPushButton { background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #DC2626; }"
        button_style_gray = "QPushButton { background-color: #6B7280; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;} QPushButton:hover { background-color: #4B5563; }"

        if is_dark:
            # Karanlık Mod Özelleştirmesi
            button_style_green = "QPushButton { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #059669; font-weight: bold;} QPushButton:hover { background-color: #047857; }"
            button_style_orange = "QPushButton { background-color: #92400E; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #D97706; font-weight: bold;} QPushButton:hover { background-color: #78350F; }"
            button_style_red = "QPushButton { background-color: #991B1B; color: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #DC2626; font-weight: bold;} QPushButton:hover { background-color: #7F1D1D; }"
            button_style_gray = "QPushButton { background-color: #374151; color: #E5E7EB; padding: 6px 12px; border-radius: 6px; border: 1px solid #4B5563; font-weight: bold;} QPushButton:hover { background-color: #4B5563; }"
            
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E5E7EB;")
            
            # Giriş Alanı Stilleri
            input_style = "padding: 6px; border: 1px solid #4B5563; border-radius: 6px; background-color: #1F2937; color: #F9FAFB;"
            self.cmb_filter_dept.setStyleSheet(f"QComboBox {{ {input_style} }} QComboBox::drop-down {{ border: none; }} QComboBox::down-arrow {{ image: none; }}") 
            self.spn_filter_year.setStyleSheet(input_style)
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #111827; color: #E5E7EB; gridline-color: #374151; border: none; alternate-background-color: #1F2937; }
                QHeaderView { background-color: #1F2937; border: none; }
                QHeaderView::section { background-color: #1F2937; color: #9CA3AF; border: none; border-bottom: 2px solid #374151; padding: 4px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #374151; color: white; }
                QTableCornerButton::section { background-color: #1F2937; border: none; }
            """)
        else:
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
            
            # Input Styles
            input_style = "padding: 6px; border: 1px solid #D1D5DB; border-radius: 6px; background-color: #FFFFFF; color: #111827;"
            self.cmb_filter_dept.setStyleSheet(input_style)
            self.spn_filter_year.setStyleSheet(input_style)
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; gridline-color: #E5E7EB; border: 1px solid #E5E7EB; alternate-background-color: #F9FAFB; }
                QHeaderView::section { background-color: #F3F4F6; color: #4B5563; border: none; border-bottom: 1px solid #E5E7EB; padding: 8px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
                QTableCornerButton::section { background-color: #F3F4F6; }
            """)

        self.btn_add.setStyleSheet(button_style_green)
        self.btn_edit.setStyleSheet(button_style_orange)
        self.btn_del.setStyleSheet(button_style_red)
        self.btn_reset.setStyleSheet(button_style_gray)
        
        self.table.setAlternatingRowColors(True)

    def load_departments(self):
        if self.lookups_loaded: return
        self.db.connect()
        try:
            depts = self.db.cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name").fetchall()
            for did, dname in depts:
                self.cmb_filter_dept.addItem(dname, did)
            self.lookups_loaded = True
        finally:
            self.db.disconnect()

    def reset_filters(self):
        self.cmb_filter_dept.setCurrentIndex(0)
        self.spn_filter_year.setValue(2025)

    def load_data(self):
        self.table.setRowCount(0)
        self.db.connect()
        try:
            filter_year = int(self.spn_filter_year.value())
            filter_dept_id = self.cmb_filter_dept.currentData()
            
            query = """
                SELECT d.department_name, b.year, b.amount, b.budget_id
                FROM budgets b
                JOIN departments d ON b.department_id = d.department_id
                WHERE b.year = ?
            """
            params = [filter_year]
            
            if filter_dept_id:
                query += " AND b.department_id = ?"
                params.append(filter_dept_id)
                
            query += " ORDER BY d.department_name ASC"
            
            self.db.cursor.execute(query, tuple(params))
            rows = self.db.cursor.fetchall()
            
            for r_idx, row in enumerate(rows):
                self.table.insertRow(r_idx)
                
                dept_name = row[0]
                # year = row[1]
                amount = row[2]
                b_id = row[3]
                
                self.table.setItem(r_idx, 0, QTableWidgetItem(str(dept_name)))
                self.table.setItem(r_idx, 1, QTableWidgetItem(f"{amount:,.2f} ₺"))
                self.table.setItem(r_idx, 2, QTableWidgetItem(str(b_id)))
                
        except Exception as e:
            print(f"Bütçe Yükleme Hatası: {e}")
        finally:
            self.db.disconnect()

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0: return # Seçim yok
        
        b_id = self.table.item(row, 2).text()
        dept = self.table.item(row, 0).text()
        
        if CustomDialogs.question(self, f"'{dept}' bütçesini silmek istediğinize emin misiniz?", "Sil"):
            self.db.connect()
            try:
                self.db.cursor.execute("DELETE FROM budgets WHERE budget_id=?", (b_id,))
                self.db.conn.commit()
                self.load_data()
            except Exception as e:
                self.db.conn.rollback()
                CustomDialogs.error(self, f"Silinemedi: {e}")
            finally:
                self.db.disconnect()

    def open_add_popup(self):
        is_dark = getattr(self, 'is_dark', False)
        year = int(self.spn_filter_year.value())
        d = BudgetPopup(self, is_dark=is_dark, default_year=year)
        if d.exec(): self.load_data()

    def open_edit_popup(self):
        row = self.table.currentRow()
        if row < 0:
            CustomDialogs.warning(self, "Lütfen düzenlenecek bütçeyi seçin.")
            return

        b_id = self.table.item(row, 2).text()
        is_dark = getattr(self, 'is_dark', False)
        d = BudgetPopup(self, is_dark=is_dark, budget_id=b_id)
        if d.exec(): self.load_data()


class BudgetPopup(QDialog):
    def __init__(self, parent=None, is_dark=False, budget_id=None, default_year=None):
        super().__init__(parent)
        self.budget_id = budget_id
        self.setWindowTitle("Yıllık Bütçe Düzenle" if budget_id else "Yeni Yıllık Bütçe")
        self.db = DatabaseManager()
        self.logger = Logger()
        layout = QFormLayout(self)
        
        self.cmb_dept = QComboBox()
        self.spn_year = QDoubleSpinBox()
        self.spn_year.setDecimals(0)
        self.spn_year.setRange(2020, 2030)
        self.spn_year.setValue(default_year if default_year else 2025)
        
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 100000000) # 100M
        self.spn_amount.setPrefix("₺ ")
        self.spn_amount.setSingleStep(1000)
        
        # Departmanları Yükle
        self.db.load_combobox_data(self.cmb_dept, "departments", "department_id", "department_name")
        
        layout.addRow("Departman:", self.cmb_dept)
        layout.addRow("Yıl:", self.spn_year)
        layout.addRow("Tutar:", self.spn_amount)
        
        btn = QPushButton("Kaydet")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        if self.budget_id:
            self.load_details()

        ThemeHelper.apply_popup_theme(self, is_dark)

    def load_details(self):
        self.db.connect()
        try:
            row = self.db.cursor.execute("SELECT department_id, year, amount FROM budgets WHERE budget_id=?", (self.budget_id,)).fetchone()
            if row:
                idx = self.cmb_dept.findData(row[0])
                if idx >= 0: self.cmb_dept.setCurrentIndex(idx)
                self.spn_year.setValue(row[1])
                self.spn_amount.setValue(row[2])
        finally:
            self.db.disconnect()

    def save(self):
        dept_id = self.cmb_dept.currentData()
        if not dept_id:
            CustomDialogs.warning(self, "Departman seçiniz.")
            return

        year = int(self.spn_year.value())
        month = 0 # ZORUNLU YILLIK (GENEL)
        amount = self.spn_amount.value()
        
        self.db.connect()
        try:
            # Mevcut GENEL bütçeyi kontrol et (Dept + Yıl + Ay=0)
            query = "SELECT budget_id FROM budgets WHERE department_id=? AND year=? AND month=?"
            params = [dept_id, year, month]
            
            if self.budget_id:
                query += " AND budget_id != ?"
                params.append(self.budget_id)
            
            exists = self.db.cursor.execute(query, tuple(params)).fetchone()
            if exists:
                CustomDialogs.warning(self, "Bu departman için seçili yıla ait Yıllık Bütçe zaten var.\nLütfen mevcut kaydı düzenleyin.", "Çakışma")
                return

            if self.budget_id:
                # Update
                self.db.cursor.execute("""
                    UPDATE budgets SET department_id=?, year=?, month=?, amount=?
                    WHERE budget_id=?
                """, (dept_id, year, month, amount, self.budget_id))
                action = "güncellendi"
            else:
                # Insert
                self.db.cursor.execute("""
                    INSERT INTO budgets (department_id, year, month, amount)
                    VALUES (?, ?, ?, ?)
                """, (dept_id, year, month, amount))
                action = "eklendi"
            
            self.db.conn.commit()
            self.logger.info(f"Yıllık Bütçe {action}: Dept={dept_id}, {year}, {amount}")
            self.accept()
        except Exception as e:
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()


class PageAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.lookups = [] # Referansları tutmak için
        self.init_ui()

    def showEvent(self, event):
        # Refresh tabs if needed
        pass

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_title = QLabel("Admin Yönetim Paneli")
        self.lbl_title.setObjectName("PageTitle")
        self.layout.addWidget(self.lbl_title)

        self.tabs = QTabWidget()
        
        # --- Sekme 1: Tanımlamalar (Lookups) ---
        self.tab_lookups = QTabWidget()
        self.tab_lookups.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_lookups.setUsesScrollButtons(True)  # Sekmeler taştığında kaydırma düğmelerini etkinleştir
        self.tab_lookups.setElideMode(Qt.TextElideMode.ElideNone)  # Sekme başlıklarını kırpma
        
        # 1. Mevcut Tanımlamalar
        l_cat = LookupEditor("categories", "category_id", "category_name", "Kategori")
        l_dept = LookupEditor("departments", "department_id", "department_name", "Departman")
        l_unit = LookupEditor("units", "unit_id", "unit_name", "Birim")
        l_role = LookupEditor("roles", "role_id", "title", "Rol")
        l_curr = LookupEditor("currencies", "currency_id", "code", "Para Birimi")
        
        self.tab_lookups.addTab(l_cat, "Kategoriler")
        self.tab_lookups.addTab(l_dept, "Departmanlar")
        self.tab_lookups.addTab(l_unit, "Birimler")
        self.tab_lookups.addTab(l_role, "Roller")
        self.tab_lookups.addTab(l_curr, "Para Birimleri")
        self.lookups.extend([l_cat, l_dept, l_unit, l_role, l_curr])
        
        # 2. Yeni Durum Tabloları
        l_req_stat = LookupEditor("request_statuses", "status_id", "status_name", "Talep Durumu")
        l_ord_stat = LookupEditor("order_statuses", "status_id", "status_name", "Sipariş Durumu")
        l_sup_stat = LookupEditor("supplier_statuses", "status_id", "status_name", "Tedarikçi Durumu")
        l_off_stat = LookupEditor("offer_statuses", "status_id", "status_name", "Teklif Durumu")
        
        self.tab_lookups.addTab(l_req_stat, "Talep Durumları")
        self.tab_lookups.addTab(l_ord_stat, "Sipariş Durumları")
        self.tab_lookups.addTab(l_sup_stat, "Tedarikçi Durumları")
        self.tab_lookups.addTab(l_off_stat, "Teklif Durumları")
        self.lookups.extend([l_req_stat, l_ord_stat, l_sup_stat, l_off_stat])
        
        # 3. Finans Tanımlamaları
        l_inv_stat = LookupEditor("invoice_statuses", "status_id", "status_name", "Fatura Durumu")
        l_pay_method = LookupEditor("payment_methods", "method_id", "method_name", "Ödeme Yöntemi")
        
        self.tab_lookups.addTab(l_inv_stat, "Fatura Durumları")
        self.tab_lookups.addTab(l_pay_method, "Ödeme Yöntemleri")
        self.lookups.extend([l_inv_stat, l_pay_method])
        
        self.tabs.addTab(self.tab_lookups, "Tanımlamalar ve Durumlar")
        
        # --- Sekme 2: Bütçe Yönetimi (YENİ) ---
        self.budget_editor = BudgetEditor()
        self.tabs.addTab(self.budget_editor, "Bütçe Yönetimi")

        # --- Sekme 3: Ürünler ---
        self.item_editor = ItemEditor()
        self.tabs.addTab(self.item_editor, "Ürün Yönetimi")

        # --- Sekme 4: Kullanıcılar ---
        self.user_editor = UserEditor()
        self.tabs.addTab(self.user_editor, "Kullanıcı Yönetimi")
        
        # --- Sekme 5: Sistem Logları ---
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True) 

        self.btn_load_logs = QPushButton("Logları Yükle")
        self.btn_load_logs.clicked.connect(self.load_logs)
        
        wid_logs = QWidget()
        l_logs = QVBoxLayout(wid_logs)
        l_logs.addWidget(self.btn_load_logs)
        l_logs.addWidget(self.txt_logs)
        self.tabs.addTab(wid_logs, "Sistem Logları")

        self.layout.addWidget(self.tabs)

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        
        # 1. Alt Sekmeleri Güncelle (Özyinelemeli)
        for lookup in self.lookups:
            if hasattr(lookup, 'update_theme'):
                lookup.update_theme(is_dark)
        
        if hasattr(self, 'item_editor'):
            self.item_editor.update_theme(is_dark)
            
        if hasattr(self, 'user_editor'):
            self.user_editor.update_theme(is_dark)
            
        if hasattr(self, 'budget_editor'):
            self.budget_editor.update_theme(is_dark)

        # 2. Ana Sekme Stillerini Güncelle
        if is_dark:
            arrow_right = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik05IDZsNiA2LTYgNiIvPjwvc3ZnPg=="
            arrow_left = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNSA2bC02IDYgNiA2Ii8+PC9zdmc+"
            
            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E5E7EB;")
            self.tabs.setStyleSheet(f"""
                QTabWidget::pane {{ border: 1px solid #374151; background: #1F2937; }}
                QTabBar::tab {{ background: #1F2937; color: #9CA3AF; padding: 8px 12px; border: 1px solid #374151; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background: #374151; color: #E5E7EB; font-weight: bold; }}
                QTabBar::scroller {{ width: 40px; }}
                QTabBar QToolButton {{ background: #374151; border: 1px solid #4B5563; border-radius: 3px; color: #E5E7EB; }}
                QTabBar QToolButton:hover {{ background: #4B5563; }}
                QTabBar QToolButton::right-arrow {{ image: url({arrow_right}); width: 12px; height: 12px; }}
                QTabBar QToolButton::left-arrow {{ image: url({arrow_left}); width: 12px; height: 12px; }}
            """)
            # İç sekme tanımlamaları kaydırma düğmeleri stili
            self.tab_lookups.setStyleSheet(f"""
                QTabWidget::pane {{ border: 1px solid #374151; background: #1F2937; }}
                QTabBar::tab {{ background: #1F2937; color: #9CA3AF; padding: 6px 10px; border: 1px solid #374151; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background: #374151; color: #E5E7EB; font-weight: bold; }}
                QTabBar::scroller {{ width: 40px; }}
                QTabBar QToolButton {{ background: #374151; border: 1px solid #4B5563; border-radius: 3px; padding: 4px; }}
                QTabBar QToolButton:hover {{ background: #4B5563; }}
                QTabBar QToolButton::right-arrow {{ image: url({arrow_right}); width: 12px; height: 12px; }}
                QTabBar QToolButton::left-arrow {{ image: url({arrow_left}); width: 12px; height: 12px; }}
            """)
            self.txt_logs.setStyleSheet("background-color: #111827; color: #E5E7EB; border: 1px solid #374151;")
            self.btn_load_logs.setStyleSheet("QPushButton { background-color: #2563EB; color: white; padding: 6px; border-radius: 4px; } QPushButton:hover { background-color: #1D4ED8; }")
        else:
            arrow_right = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMjc0MTUxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTkgNmw2IDYtNiA2Ii8+PC9zdmc+"
            arrow_left = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMjc0MTUxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTE1IDZsLTYgNiA2IDYiLz48L3N2Zz4="

            self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827;")
            self.tabs.setStyleSheet(f"""
                QTabWidget::pane {{ border: 1px solid #E5E7EB; background: #FFFFFF; }}
                QTabBar::tab {{ background: #F3F4F6; color: #4B5563; padding: 8px 12px; border: 1px solid #E5E7EB; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background: #FFFFFF; color: #1F2937; font-weight: bold; border-bottom: 2px solid #2563EB; }}
                QTabBar::scroller {{ width: 40px; }}
                QTabBar QToolButton {{ background: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 3px; padding: 4px; }}
                QTabBar QToolButton:hover {{ background: #E5E7EB; }}
                QTabBar QToolButton::right-arrow {{ image: url({arrow_right}); width: 12px; height: 12px; }}
                QTabBar QToolButton::left-arrow {{ image: url({arrow_left}); width: 12px; height: 12px; }}
            """)
            # İç sekme tanımlamaları için aydınlık mod
            self.tab_lookups.setStyleSheet(f"""
                QTabWidget::pane {{ border: 1px solid #E5E7EB; background: #FFFFFF; }}
                QTabBar::tab {{ background: #F3F4F6; color: #4B5563; padding: 6px 10px; border: 1px solid #E5E7EB; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background: #FFFFFF; color: #1F2937; font-weight: bold; }}
                QTabBar::scroller {{ width: 40px; }}
                QTabBar QToolButton {{ background: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 3px; padding: 4px; }}
                QTabBar QToolButton:hover {{ background: #E5E7EB; }}
                QTabBar QToolButton::right-arrow {{ image: url({arrow_right}); width: 12px; height: 12px; }}
                QTabBar QToolButton::left-arrow {{ image: url({arrow_left}); width: 12px; height: 12px; }}
            """)
            self.txt_logs.setStyleSheet("background-color: #F9FAFB; color: #111827; border: 1px solid #E5E7EB;")
            self.btn_load_logs.setStyleSheet("QPushButton { background-color: #3B82F6; color: white; padding: 6px; border-radius: 4px; } QPushButton:hover { background-color: #2563EB; }")

    def load_logs(self):
        import os
        # Logger sınıfından dinamik yolu al
        log_dir = Logger().log_dir
        log_path = os.path.join(log_dir, "application.log")
        
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Son 10.000 karakteri oku
                f.seek(0, os.SEEK_END)
                size = f.tell()
                if size > 10000:
                    f.seek(size - 10000)
                else:
                    f.seek(0)
                content = f.read()
                self.txt_logs.setText(content)
                # En alta kaydır
                self.txt_logs.verticalScrollBar().setValue(self.txt_logs.verticalScrollBar().maximum())
        else:
            self.txt_logs.setText(f"Log dosyası bulunamadı:\n{log_path}")
