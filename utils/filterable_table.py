from PyQt6.QtWidgets import (QHeaderView, QPushButton, QDialog, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem, 
                             QDialogButtonBox, QCheckBox, QWidget, QApplication, QLabel, QFrame, QAbstractItemView)

from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QIcon, QPainter, QColor
from datetime import datetime
import locale

from utils.theme_helper import ThemeHelper

class FilterPopup(QDialog):
    def __init__(self, parent, column_index, unique_values, current_filters, is_dark=False):
        super().__init__(parent)
        self.column_index = column_index
        self.all_values = unique_values
        self.is_dark = is_dark
        self.header_parent = parent 
        
        if is_dark:
            self.bg_color = "#1F2937"    
            self.text_color = "#E5E7EB" 
            self.input_bg = "#374151"
            self.border_color = "#4B5563"
            self.hover_color = "#374151"
            self.btn_bg = "#111827"
            self.btn_hover = "#374151"
        else:
            self.bg_color = "#FFFFFF"
            self.text_color = "#111827"
            self.input_bg = "#FFFFFF"
            self.border_color = "#D1D5DB"
            self.hover_color = "#F3F4F6"
            self.btn_bg = "#F9FAFB"
            self.btn_hover = "#E5E7EB"

        self.setWindowTitle("Filtrele")
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.resize(260, 420)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.setStyleSheet(f"""
            QDialog {{ 
                background-color: {self.bg_color}; 
                color: {self.text_color}; 
                border: 1px solid {self.border_color}; 
                border-radius: 6px;
            }}
            QLineEdit {{ 
                background-color: {self.input_bg}; 
                color: {self.text_color}; 
                border: 1px solid {self.border_color}; 
                padding: 6px; 
                border-radius: 4px; 
            }}
            QTreeWidget {{ 
                background-color: {self.input_bg}; 
                color: {self.text_color}; 
                border: 1px solid {self.border_color}; 
                border-radius: 4px; 
                outline: none; 
            }}
            QTreeWidget::item {{ 
                color: {self.text_color}; 
                padding: 5px; 
            }}
            QTreeWidget::item:hover {{ 
                background-color: {self.hover_color}; 
            }}
            QTreeWidget::item:selected {{ 
                background-color: transparent; 
                color: {self.text_color}; 
            }}
            
            /* BİRLEŞTİRİLMİŞ ONAY KUTUSU STİLİ */
            QCheckBox, QListView {{
                color: {self.text_color};
            }}
            QCheckBox::indicator, QListView::indicator {{ 
                width: 18px; 
                height: 18px; 
                border: 1px solid {self.border_color}; 
                border-radius: 4px; 
                background-color: {self.input_bg}; 
            }}
            QCheckBox::indicator:hover, QListView::indicator:hover {{
                border-color: #3B82F6;
            }}
            QCheckBox::indicator:checked, QListView::indicator:checked {{ 
                background-color: #2563EB; 
                border-color: #2563EB; 
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlX3dpZHRoPSIzaCIgc3Ryb2tlX2xpbmVjYXA9InJvdW5kIiBzdHJva2VfbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=); 
            }}
            
            QPushButton {{
                background-color: {self.btn_bg};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.btn_hover};
            }}
        """)
        

        sort_layout = QHBoxLayout()
        
        btn_sort_asc = QPushButton("Artan Sırala (A-Z)")
        btn_sort_asc.setIcon(QIcon(":/icons/sort_asc.png"))
        btn_sort_asc.clicked.connect(lambda: self.apply_sort(Qt.SortOrder.AscendingOrder))
        
        btn_sort_desc = QPushButton("Azalan Sırala (Z-A)")
        btn_sort_desc.clicked.connect(lambda: self.apply_sort(Qt.SortOrder.DescendingOrder))
        
        sort_layout.addWidget(btn_sort_asc)
        sort_layout.addWidget(btn_sort_desc)
        layout.addLayout(sort_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {self.border_color}; max-height: 1px;")
        layout.addWidget(line)

        # --- FİLTRELEME ---
        # Arama Kutusu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ara...")
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)

        # Tümünü Seç Onay Kutusu
        self.cb_select_all = QCheckBox(" Tümünü Seç")
        self.cb_select_all.setChecked(True) # Varsayılan olarak hepsi seçili
        self.cb_select_all.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(self.cb_select_all)

        # Filtre Listesi (Ağaç Bileşeni)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        # self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) # Çoklu seçim mantığı manuel olarak kontrol kutuları ile işlenir
        layout.addWidget(self.tree_widget)

        # Buttons
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Tamam")
        btn_ok.setStyleSheet("background-color: #2563EB; color: white; border: none;")
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

        # Listeyi Doldur
        self.populate_tree(current_filters)
        
        self.update_select_all_state()

        # Öğe Değişiklik Sinyalini Bağla
        self.tree_widget.itemChanged.connect(self.on_item_changed)

    def populate_tree(self, current_filters):
        self.tree_widget.blockSignals(True)
        self.tree_widget.clear()
        
        # all_values Sözlük (Gruplanmış) mü yoksa Liste (Düz) mi kontrol et
        if isinstance(self.all_values, dict):
            # Gruplanmış (Tarih)
            # Anahtarları Sırala (Aylar) - doğru hazırlanırsa "Yıl-Ay" anahtarları için daha basit alfasayısal sıralama, 
            # ancak genellikle anahtarlar "AyAdı Yıl" şeklindedir. Giriş sırasına güvenebilir veya mümkünse tarihe göre sıralayabiliriz.
            # Anahtarların mantıklı bir sırada geçtiğini varsayıyoruz veya kesin alfabetik sıralama yapıyoruz:
            for group_name in sorted(self.all_values.keys()): # Basit sıralama, daha sonra geliştirilebilir
                parent_item = QTreeWidgetItem(self.tree_widget)
                parent_item.setText(0, group_name)
                parent_item.setFlags(parent_item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
                parent_item.setCheckState(0, Qt.CheckState.Unchecked)
                
                # Alt öğeler
                children_values = self.all_values[group_name]
                for val in sorted(children_values):
                     child = QTreeWidgetItem(parent_item)
                     child.setText(0, str(val))
                     child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                     
                     if current_filters is None or str(val) in current_filters:
                         child.setCheckState(0, Qt.CheckState.Checked)
                     else:
                         child.setCheckState(0, Qt.CheckState.Unchecked)
            self.tree_widget.expandAll()
            
        else:
            # Düz Liste
            for val in sorted(self.all_values):
                 item = QTreeWidgetItem(self.tree_widget)
                 item.setText(0, str(val))
                 item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                 if current_filters is None or str(val) in current_filters:
                     item.setCheckState(0, Qt.CheckState.Checked)
                 else:
                     item.setCheckState(0, Qt.CheckState.Unchecked)
        
        self.tree_widget.blockSignals(False)

    def apply_sort(self, order):
        # Üst tabloyu sırala
        self.header_parent.parent_table.sortItems(self.column_index, order)
        self.reject() # Pencereyi kapat, sıralama düğmeleriyle filtre uygulanmadı, ancak sıralama uygulandı

    def filter_list(self, text):
        text = text.lower()
        # Ağacı dolaş
        root = self.tree_widget.invisibleRootItem()
        child_count = root.childCount()
        
        for i in range(child_count):
            item = root.child(i)
            # Grup mu Yaprak mı kontrol et
            if item.childCount() > 0:
                # Grup
                has_visible_child = False
                for j in range(item.childCount()):
                    child = item.child(j)
                    if text in child.text(0).lower():
                        child.setHidden(False)
                        has_visible_child = True
                    else:
                        child.setHidden(True)
                
                # Üst öğe gizlenmeli mi? 
                # Eğer üst öğe metinle eşleşirse, tüm çocukları göster? Yoksa sadece eşleşen çocukları mı göster?
                # Genellikle: Üst eşleşirse hepsini göster. Çocuk eşleşirse üst + çocuk göster.
                if text in item.text(0).lower():
                    # Tüm alt öğeleri göster
                    item.setHidden(False)
                    for j in range(item.childCount()):
                        item.child(j).setHidden(False)
                else:
                     item.setHidden(not has_visible_child)
            else:
                # Yaprak (Düz mod)
                item.setHidden(text not in item.text(0).lower())

    def toggle_select_all(self, state):
        self.tree_widget.blockSignals(True)
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked)
                # Grup ise, alt öğeler genellikle Tristate bayrağı nedeniyle otomatik güncellenir, ancak gizli durumlar için emin olalım
                if item.childCount() > 0:
                     for j in range(item.childCount()):
                         child = item.child(j)
                         if not child.isHidden():
                              child.setCheckState(0, Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked)
        self.tree_widget.blockSignals(False)

    def on_item_changed(self, item, column):
        self.update_select_all_state()

    def update_select_all_state(self):
        # Görünür tüm öğelerin seçili olup olmadığını kontrol et
        all_checked = True
        has_visible_items = False
        
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if not item.isHidden():
                has_visible_items = True
                
                # Grup ise, Tristate görseli halleder, ancak durumu kontrol ediyoruz
                if item.checkState(0) == Qt.CheckState.Unchecked or item.checkState(0) == Qt.CheckState.PartiallyChecked:
                    all_checked = False
                    break
        
        self.cb_select_all.blockSignals(True)
        if has_visible_items and all_checked:
            self.cb_select_all.setCheckState(Qt.CheckState.Checked)
        else:
            self.cb_select_all.setCheckState(Qt.CheckState.Unchecked)
        self.cb_select_all.blockSignals(False)

    def get_selected_values(self):
        selected = []
        root = self.tree_widget.invisibleRootItem()
        # Hepsini dolaş
        stack = [root.child(i) for i in range(root.childCount())]
        while stack:
            item = stack.pop(0)
            if item.childCount() > 0:
                # Bu bir grup, çocukları yığına ekle
                # Seçilenlere grup metnini EKLEMİYORUZ, sadece yaprakları
                for i in range(item.childCount()):
                    stack.append(item.child(i))
            else:
                # Bu bir yaprak
                if item.checkState(0) == Qt.CheckState.Checked:
                    selected.append(item.text(0))
        return selected


class FilterHeader(QHeaderView):
    filter_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.sectionClicked.connect(self.on_section_clicked)
        
        self.active_filters = {} 
        self.parent_table = parent
        self.sort_order = Qt.SortOrder.AscendingOrder # Doğrudan tıklamalar için sıralama düzenini takip et

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        # Boyama için hariç tutmayı kontrol et
        is_excluded = False
        header_item = self.parent_table.horizontalHeaderItem(logicalIndex)
        if header_item:
             header_text = header_item.text().lower()
             excluded_keywords = ["id", "miktar", "fiyat", "tutar", "toplam"]
             if any(k in header_text for k in excluded_keywords):
                 is_excluded = True

        if not is_excluded:
            # Filtrenin etkin olup olmadığını kontrol et
            is_filtered = logicalIndex in self.active_filters and self.active_filters[logicalIndex] is not None
            
            # Boyama için tema mantığını belirle
            is_dark = False
            top_lvl = self.window()
            if hasattr(top_lvl, 'is_dark_mode'):
                is_dark = top_lvl.is_dark_mode
            elif hasattr(top_lvl, 'is_dark'):
                is_dark = top_lvl.is_dark

            if is_filtered:
                painter.save()
                # Görsel gösterge arka planını çiz
                if is_dark:
                    bg_color = QColor(251, 191, 36, 60) # Kehribar-400 şeffaf
                    icon_color = QColor(251, 191, 36)   # Kehribar-400
                else:
                    bg_color = QColor(252, 211, 77, 100) # Kehribar-300 şeffaf
                    icon_color = QColor(245, 158, 11)    # Kehribar-600

                painter.fillRect(rect, bg_color)
                painter.setPen(icon_color)
                
                # Dolu Huni benzeri şekil çiz veya sadece Kalın Ok
                # Özel ikon varlıkları garanti edilmediğinden, metne sadık kalıyoruz ancak daha koyu renkte
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                
                icon_rect = QRect(rect.right() - 20, rect.top() + (rect.height() - 20) // 2, 20, 20)
                painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "▼") # ★ or similar could be used too
                painter.restore()
            else:
                # Varsayılan Gri Ok
                painter.save()
                painter.setPen(QColor("#9CA3AF"))
                icon_rect = QRect(rect.right() - 20, rect.top() + (rect.height() - 20) // 2, 20, 20)
                painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "▼")
                painter.restore()

    def on_section_clicked(self, logicalIndex):
        # Temayı belirle
        is_dark = False
        top_lvl = self.window()
        if hasattr(top_lvl, 'is_dark_mode'):
            is_dark = top_lvl.is_dark_mode
        elif hasattr(top_lvl, 'is_dark'):
            is_dark = top_lvl.is_dark

        # HARİÇ TUTMA MANTIĞI
        # Sayısal sütun ise, pencere yerine standart SIRALAMA yap
        header_item = self.parent_table.horizontalHeaderItem(logicalIndex)
        if header_item:
            header_text = header_item.text().lower()
            excluded_keywords = ["id", "miktar", "fiyat", "tutar", "toplam"]
            if any(k in header_text for k in excluded_keywords):
                # Standart Sıralama Davranışı
                # Sırayı değiştir
                if self.sort_order == Qt.SortOrder.AscendingOrder:
                    self.sort_order = Qt.SortOrder.DescendingOrder
                else:
                    self.sort_order = Qt.SortOrder.AscendingOrder
                
                self.parent_table.sortItems(logicalIndex, self.sort_order)
                return
        
        # Mevcut filtreleri ve geçerli değerleri belirle
        values_raw = set()
        for row in range(self.parent_table.rowCount()):
            item = self.parent_table.item(row, logicalIndex)
            if item:
                values_raw.add(item.text())
        
        # TARİH gruplaması gerekli mi kontrol et
        header_text_lower = header_item.text().lower()
        if "tarih" in header_text_lower or "created" in header_text_lower:
            # Ayrıştırmayı ve gruplamayı dene
            grouped_data = {} # {"Ocak 2024": ["01.01.2024", ...]}
            flat_fallback = False
            
            # Türkçe Ay Eşleştirmesi (yerel ayar güvenilir değilse)
            tr_months = {
                1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
            }
            
            for val in values_raw:
                try:
                    # Yaygın formatları dene
                    dt = None
                    try:
                         dt = datetime.strptime(val, "%d.%m.%Y")
                    except ValueError:
                         try:
                             dt = datetime.strptime(val, "%Y-%m-%d")
                         except ValueError:
                             pass
                    
                    if dt:
                        month_key = f"{tr_months.get(dt.month)} {dt.year}"
                        if month_key not in grouped_data:
                            grouped_data[month_key] = []
                        grouped_data[month_key].append(val)
                    else:
                        # Birisi için ayrıştırma başarısız olursa, düze sadık kal? veya "Diğer" altında grupla?
                        # Geçerli tarihleri grup, geçersizleri "Diğer" olarak ele alalım
                        if "Diğer" not in grouped_data: grouped_data["Diğer"] = []
                        grouped_data["Diğer"].append(val)
                        
                except Exception:
                     flat_fallback = True
                     break
            
            # grouped_data anahtarlarını tarihe göre sırala
            # "Ocak 2024"ü sıralama için tarihe geri ayrıştıran yardımcı
            def sort_key_func(k):
                if k == "Diğer": return datetime.min
                parts = k.split()
                if len(parts) == 2:
                    month_name = parts[0]
                    year = int(parts[1])
                    # tr_months'ı ters çevir
                    month_num = 1
                    for m_num, m_name in tr_months.items():
                        if m_name == month_name:
                            month_num = m_num
                            break
                    return datetime(year, month_num, 1)
                return datetime.min

            # Sıralanmış sözlüğü geçmeliyiz veya FilterPopup'ın sıralamasına izin vermeliyiz.
            # Sözlükler yeni Python'da sıralamayı etkinleştirir, ancak sadece sözlüğü geçelim.
            # FilterPopup mantığı anahtarları yineleyecektir. Belki bir demet listesi geçmeliyiz?
            # Veya FilterPopup anahtarları sıralar.
            
            values_to_pass = grouped_data
        else:
            values_to_pass = sorted(list(values_raw))

        current_filter = self.active_filters.get(logicalIndex)
        
        popup = FilterPopup(self, logicalIndex, values_to_pass, current_filter, is_dark=is_dark)
        
        x_pos = self.sectionViewportPosition(logicalIndex)
        pos = self.viewport().mapToGlobal(QPoint(x_pos, self.height()))
        popup.move(pos)

        if popup.exec():
            selected = popup.get_selected_values()
            
            # Toplam yaprak değerlerini say
            total_values_count = len(values_raw)
            
            if len(selected) == total_values_count and total_values_count > 0:
                if logicalIndex in self.active_filters:
                    del self.active_filters[logicalIndex]
            else:
                self.active_filters[logicalIndex] = selected
            
            self.apply_filters()

    def apply_filters(self):
        rows = self.parent_table.rowCount()
        for row in range(rows):
            should_show = True
            for col, allowed_vals in self.active_filters.items():
                item = self.parent_table.item(row, col)
                val = item.text() if item else ""
                
                if val not in allowed_vals:
                    should_show = False
                    break
            
            self.parent_table.setRowHidden(row, not should_show)

    def clear_filters(self):
        """Tüm filtreleri temizler ve tabloyu varsayılan haline döndürür."""
        self.active_filters.clear()
        
        # Tüm satırları göster
        rows = self.parent_table.rowCount()
        for row in range(rows):
            self.parent_table.setRowHidden(row, False)
            
        # Header'ı yeniden çiz (ikonları kaldırmak için)
        self.viewport().update()

