from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QProgressBar,
                             QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QColor, QBrush
from database.db_manager import DatabaseManager
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from utils.currency_fetcher import CurrencyFetcher

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        # Başlangıcı engellememek için veri çekmeyi geciktir
        QTimer.singleShot(100, self.refresh_stats)

    def showEvent(self, event):
        self.refresh_stats()
        super().showEvent(event)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # TITLE
        self.lbl_title = QLabel("Genel Bakış")
        self.lbl_title.setObjectName("PageTitle")
        self.layout.addWidget(self.lbl_title)

        # 1. METRİK KARTLARI SATIRI
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.card_total = self.create_card("Aylık Sipariş", "0", "card_blue")
        self.card_pending = self.create_card("Açık Talepler", "0", "card_orange")
        self.card_expense = self.create_card("Aylık Harcama", "0 ₺", "card_green")
        self.card_suppliers = self.create_card("Aktif Tedarikçi", "0", "card_purple")
        
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_pending)
        cards_layout.addWidget(self.card_expense)
        cards_layout.addWidget(self.card_suppliers)
        
        self.layout.addLayout(cards_layout)

        # 1.5 FİNANS WIDGETLARI SATIRI (Bütçe & Gecikmiş)
        finance_layout = QHBoxLayout()
        finance_layout.setSpacing(20)

        # Departman Bütçe Durumu (Mini Bar veya İlerleme)
        self.card_budget = QFrame()
        self.card_budget.setObjectName("BudgetFrame")
        budget_layout = QVBoxLayout(self.card_budget)
        lbl_bud_title = QLabel("Departman Bütçe Durumu (Bu Yıl)")
        lbl_bud_title.setObjectName("WidgetTitle")
        lbl_bud_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        
        lbl_bud_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        
        # Dinamik İlerleme Çubukları için Konteyner
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedHeight(150) # 4 items * ~38px
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;") # Transparent

        self.budget_content_widget = QWidget()
        self.budget_content_widget.setStyleSheet("background: transparent;")
        
        self.budget_content_layout = QVBoxLayout(self.budget_content_widget)
        self.budget_content_layout.setContentsMargins(0, 0, 0, 0)
        self.budget_content_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.budget_content_widget)
        
        budget_layout.addWidget(lbl_bud_title)
        budget_layout.addWidget(self.scroll_area)
        
        # Gecikmiş Ödemeler Uyarısı
        self.card_overdue = QFrame()
        self.card_overdue.setObjectName("OverdueFrame")
        overdue_layout = QVBoxLayout(self.card_overdue)
        lbl_over_title = QLabel("📢 Vadesi Geçen / Yaklaşan Ödemeler")
        lbl_over_title.setObjectName("WidgetTitle")
        lbl_over_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        
        self.lbl_overdue_info = QLabel("Yükleniyor...")
        self.lbl_overdue_info.setObjectName("WidgetValue")
        self.lbl_overdue_info.setWordWrap(True)

        overdue_layout.addWidget(lbl_over_title)
        overdue_layout.addWidget(self.lbl_overdue_info)
        overdue_layout.addStretch()

        finance_layout.addWidget(self.card_budget)
        finance_layout.addWidget(self.card_overdue)
        
        self.layout.addLayout(finance_layout)

        # 2. GRAFİKLER & SON ETKİNLİK SATIRI
        # 2 sütuna böl: Sol (Grafikler), Sağ (Son Liste)
        content_split = QHBoxLayout()
        content_split.setSpacing(20)

        # -- Sol Sütun: Grafikler --
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        
        # Pie & Bar side by side
        # Pasta & Çubuk yan yana
        charts_row = QHBoxLayout()
        
        # -- Pasta Grafiği Konteyneri --
        pie_container = QFrame()
        pie_container.setObjectName("ChartFrame")
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_pie_title = QLabel("Sipariş Durumları")
        self.lbl_pie_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pie_title.setObjectName("ChartTitle")
        self.lbl_pie_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        
        self.pie_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.pie_ax = self.pie_canvas.figure.subplots()
        
        pie_layout.addWidget(self.lbl_pie_title)
        pie_layout.addWidget(self.pie_canvas)
        charts_row.addWidget(pie_container)
        
        # -- Çubuk Grafiği Konteyneri --
        bar_container = QFrame()
        bar_container.setObjectName("ChartFrame")
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_bar_title = QLabel("Aylık Harcama")
        self.lbl_bar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_bar_title.setObjectName("ChartTitle")
        self.lbl_bar_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        
        self.bar_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.bar_ax = self.bar_canvas.figure.subplots()
        
        bar_layout.addWidget(self.lbl_bar_title)
        bar_layout.addWidget(self.bar_canvas)
        charts_row.addWidget(bar_container)
        
        charts_layout.addLayout(charts_row)
        content_split.addWidget(charts_container, stretch=2)

        # -- Sağ Sütun: Son Etkinlik --
        recent_container = QFrame()
        recent_container.setObjectName("RecentFrame")
        recent_layout = QVBoxLayout(recent_container)
        
        lbl_recent = QLabel("Son 5 Sipariş")
        lbl_recent.setObjectName("RecentTitle")
        lbl_recent.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        recent_layout.addWidget(lbl_recent)
        
        self.tbl_recent = QTableWidget()
        self.tbl_recent.setColumnCount(3)
        self.tbl_recent.setHorizontalHeaderLabels(["Sipariş ID", "Tedarikçi", "Tutar"])
        self.tbl_recent.horizontalHeader().setVisible(False)
        self.tbl_recent.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_recent.verticalHeader().setVisible(False)
        self.tbl_recent.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_recent.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl_recent.setShowGrid(False)
        self.tbl_recent.setStyleSheet("background: transparent; border: none;")
        recent_layout.addWidget(self.tbl_recent)
        
        content_split.addWidget(recent_container, stretch=1)

        self.layout.addLayout(content_split)
        
        # Spacer
        self.layout.addStretch()

    def create_card(self, title, value, object_name):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_val = QLabel(value)
        lbl_val.setObjectName("CardValue")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("CardTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(lbl_val)
        layout.addWidget(lbl_title)
        return frame

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        bg_color = "#1F2937" if is_dark else "#FFFFFF"
        text_color = "#E5E7EB" if is_dark else "#111827"
        
        self.lbl_title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text_color};")
        
        # Kartlar için Gradyanlar
        # Mavi: Toplam Sipariş
        # Turuncu: Bekleyen
        # Yeşil: Harcama
        # Purple: Suppliers
        
        # Ortak Kart CSS
        base_card = "border-radius: 15px; color: white;"
        
        self.card_total.setStyleSheet(f"""
            QFrame#card_blue {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3B82F6, stop:1 #2563EB); {base_card} }}
            QLabel {{ background: transparent; color: white; }}
            QLabel#CardValue {{ font-size: 32px; font-weight: bold; }}
            QLabel#CardTitle {{ font-size: 14px; opacity: 0.8; }}
        """)
        
        self.card_pending.setStyleSheet(f"""
            QFrame#card_orange {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F59E0B, stop:1 #D97706); {base_card} }}
            QLabel {{ background: transparent; color: white; }}
            QLabel#CardValue {{ font-size: 32px; font-weight: bold; }}
            QLabel#CardTitle {{ font-size: 14px; opacity: 0.8; }}
        """)
        
        self.card_expense.setStyleSheet(f"""
            QFrame#card_green {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10B981, stop:1 #059669); {base_card} }}
            QLabel {{ background: transparent; color: white; }}
            QLabel#CardValue {{ font-size: 32px; font-weight: bold; }}
            QLabel#CardTitle {{ font-size: 14px; opacity: 0.8; }}
        """)
        
        self.card_suppliers.setStyleSheet(f"""
            QFrame#card_purple {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8B5CF6, stop:1 #7C3AED); {base_card} }}
            QLabel {{ background: transparent; color: white; }}
            QLabel#CardValue {{ font-size: 32px; font-weight: bold; }}
            QLabel#CardTitle {{ font-size: 14px; opacity: 0.8; }}
        """)
        
        # Son Liste Teması
        if is_dark:
            self.findChild(QFrame, "RecentFrame").setStyleSheet("background-color: #1F2937; border-radius: 15px; border: 1px solid #374151;")
            self.findChild(QLabel, "RecentTitle").setStyleSheet("color: #E5E7EB; border: none;")
            
            # Grafik Çerçevesi Teması
            for frame in self.findChildren(QFrame, "ChartFrame"):
                frame.setStyleSheet("background-color: #1F2937; border-radius: 15px; border: 1px solid #374151;")

            self.tbl_recent.setStyleSheet("color: #E5E7EB; gridline-color: transparent; background: transparent;")
            
            # Grafik Etiketleri
            self.lbl_pie_title.setStyleSheet("color: #E5E7EB; font-size: 14px; font-weight: bold; margin-bottom: 5px; border: none;")
            self.lbl_bar_title.setStyleSheet("color: #E5E7EB; font-size: 14px; font-weight: bold; margin-bottom: 5px; border: none;")
        else:
            self.findChild(QFrame, "RecentFrame").setStyleSheet("background-color: #FFFFFF; border-radius: 15px; border: 1px solid #E5E7EB;")
            self.findChild(QLabel, "RecentTitle").setStyleSheet("color: #111827; border: none;")
            
            # Chart Frame Theme
            for frame in self.findChildren(QFrame, "ChartFrame"):
                 frame.setStyleSheet("background-color: #FFFFFF; border-radius: 15px; border: 1px solid #E5E7EB;")

            self.tbl_recent.setStyleSheet("color: #1F2937; gridline-color: transparent; background: transparent;")

            # Chart Labels
            self.lbl_pie_title.setStyleSheet("color: #111827; font-size: 14px; font-weight: bold; margin-bottom: 5px; border: none;")
            self.lbl_bar_title.setStyleSheet("color: #111827; font-size: 14px; font-weight: bold; margin-bottom: 5px; border: none;")

        # FİNANS WIDGETLARI TEMASI
        if is_dark:
            self.card_budget.setStyleSheet("background-color: #1F2937; border-radius: 12px; border: 1px solid #374151;")
            self.card_overdue.setStyleSheet("background-color: #1F2937; border-radius: 12px; border: 1px solid #374151;")
            self.findChild(QLabel, "WidgetTitle").setStyleSheet("color: #E5E7EB; border: none;")
            self.findChild(QLabel, "WidgetValue").setStyleSheet("color: #D1D5DB; font-size: 13px; border: none;")
        else:
            self.card_budget.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E5E7EB;")
            self.card_overdue.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E5E7EB;")
            self.findChild(QLabel, "WidgetTitle").setStyleSheet("color: #111827; border: none;")
            self.findChild(QLabel, "WidgetValue").setStyleSheet("color: #374151; font-size: 13px; border: none;")
        
        # Gerekirse Bütçe Düzeni içindeki dinamik etiketleri güncelle
        # Yenilendiğinde yeniden oluşturulduğu için anlık stil güncellemesi gerekebilir?
        # refresh_stats yeterince sık mı çağrılıyor? Hayır, genelde bir kez.
        # Ancak create_card / refresh_stats PBar stilini satır içi ayarlar.
        # Yine de Etiketler (Ad/Oran) metin rengi güncellemesine ihtiyaç duyar.
        if hasattr(self, 'budget_content_layout'):
            for i in range(self.budget_content_layout.count()):
                w = self.budget_content_layout.itemAt(i).widget()
                if w:
                    for lbl in w.findChildren(QLabel):
                        lbl.setStyleSheet(f"color: {text_color}; border: none; font-size: 12px;")

        # Grafik Teması
        for canvas, ax in [(self.pie_canvas, self.pie_ax), (self.bar_canvas, self.bar_ax)]:
            canvas.figure.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            ax.title.set_color(text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.tick_params(colors=text_color)
            for spine in ax.spines.values():
                spine.set_edgecolor(text_color)
                
        # Pasta Grafiği Kenar Rengi
        if is_dark:
            self.pie_edge_color = "#FFFFFF" # Match background (invisible)
        else:
            self.pie_edge_color = "#5a6e82" # Sidebar color for Light Mode
            
        self.refresh_charts()

    def refresh_stats(self):
        self.db.connect()
        try:
            # 0. Canlı Kurları Getir
            rates = CurrencyFetcher.get_rates()
            # Eğer getirme tamamen başarısız olursa varsayılan yedek değerler
            if 'USD' not in rates: rates['USD'] = 1.0 
            if 'EUR' not in rates: rates['EUR'] = 1.0
            
            # 1. Aylık Sipariş (Bu Ay)
            total = self.db.cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE strftime('%Y-%m', delivery_date) = strftime('%Y-%m', 'now')").fetchone()[0]
            
            # 2. Açık Talepler (Talepler -> Bekliyor)
            pending = self.db.cursor.execute("""
                SELECT COUNT(*) FROM purchase_requests pr 
                JOIN request_statuses st ON pr.status_id = st.status_id 
                WHERE st.status_name = 'Bekliyor'
            """).fetchone()[0]
            
            # 3. Aylık Harcama (Sadece Bu Ay)
            # Mümkünse purchase_orders tablosunda saklanan döviz kurunu kullan, yoksa yedekle
            # Yukarıdaki sorgu fiyat, miktar, kodu seçer.
            # Daha iyisi: Doğrudan (fiyat * miktar * kur) seç.
             
            total_spend_try = 0.0
            rows = self.db.cursor.execute("""
                SELECT SUM(off.price * pr.quantity * po.exchange_rate)
                FROM purchase_orders po
                JOIN offers off ON po.offer_id = off.offer_id
                JOIN purchase_requests pr ON off.request_id = pr.request_id
                WHERE strftime('%Y-%m', po.delivery_date) = strftime('%Y-%m', 'now')
            """).fetchone()
            
            if rows and rows[0]:
                total_spend_try = rows[0]
            
            # 4. Aktif Tedarikçi
            suppliers = self.db.cursor.execute("SELECT COUNT(*) FROM suppliers WHERE status_id = (SELECT status_id FROM supplier_statuses WHERE status_name='Aktif')").fetchone()[0]

            self.card_total.findChild(QLabel, "CardValue").setText(str(total))
            self.card_pending.findChild(QLabel, "CardValue").setText(str(pending))
            self.card_expense.findChild(QLabel, "CardValue").setText(f"{total_spend_try:,.0f} ₺")
            self.card_suppliers.findChild(QLabel, "CardValue").setText(str(suppliers))
            
            # --- 5. FİNANS WIDGETLARI VERİSİ ---
            
            # A) Departman Bütçe Durumu (İlk 3-4 Departman)
            try:
                current_year = QDate.currentDate().year()
                
                # Departman Başına Bütçeleri Getir
                # d.department_name, b.amount
                budgets = self.db.cursor.execute("""
                    SELECT d.department_id, d.department_name, SUM(b.amount)
                    FROM budgets b
                    JOIN departments d ON b.department_id = d.department_id
                    WHERE b.year = ?
                    GROUP BY d.department_id
                """, (current_year,)).fetchall()
                
                # Sözlük: {dept_id: {'name': 'IT', 'budget': 1000, 'spent': 0}}
                dept_map = {}
                for bid, bname, bamt in budgets:
                    dept_map[bid] = {'name': bname, 'budget': bamt, 'spent': 0.0}
                    
                # Departman Başına Harcamayı Getir
                # u.department_id'ye göre grupla
                # Düzeltme: Bütçe oluşturma mantığıyla eşleşmesi için canlı kurlar yerine saklanan po.exchange_rate kullan
                spending = self.db.cursor.execute("""
                    SELECT u.department_id, SUM(o.price * pr.quantity * po.exchange_rate)
                    FROM purchase_orders po
                    JOIN offers o ON po.offer_id = o.offer_id
                    JOIN purchase_requests pr ON o.request_id = pr.request_id
                    JOIN users u ON pr.requester_user_id = u.user_id
                    WHERE strftime('%Y', po.created_at) = ? AND po.status_id IN (SELECT status_id FROM order_statuses WHERE status_name != 'İptal')
                    GROUP BY u.department_id
                """, (str(current_year),)).fetchall()
                
                for did, amt in spending:
                    if did in dept_map:
                        dept_map[did]['spent'] = amt
                    
                # Düzendeki mevcut öğeleri temizle
                while self.budget_content_layout.count():
                    child = self.budget_content_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                # Kullanım Oranına göre azalan sırala
                sorted_depts = sorted(dept_map.values(), key=lambda x: (x['spent']/x['budget'] if x['budget']>0 else 0), reverse=True)
                
                # HEPSİNİ Al (Artık Kaydırılabilir)
                if not sorted_depts:
                     lbl_none = QLabel("<i>Henüz bütçe verisi yok.</i>")
                     self.budget_content_layout.addWidget(lbl_none)
                else:
                    for d in sorted_depts:
                        name = d['name']
                        b = d['budget']
                        s = d['spent']
                        ratio = (s / b * 100) if b > 0 else 0
                        
                        # Satır Konteyneri
                        row_widget = QWidget()
                        row_layout = QVBoxLayout(row_widget)
                        row_layout.setContentsMargins(0, 0, 0, 0)
                        row_layout.setSpacing(2)
                        
                        # Başlık (İsim + Oran)
                        header_layout = QHBoxLayout()
                        lbl_name = QLabel(f"<b>{name}</b>")
                        lbl_val = QLabel(f"%{ratio:.0f} ({s:,.0f}₺ / {b:,.0f}₺)")
                        # Temaya göre metin rengini belirle? Global stile güveneceğiz
                        
                        header_layout.addWidget(lbl_name)
                        header_layout.addStretch()
                        header_layout.addWidget(lbl_val)
                        
                        # İlerleme Çubuğu
                        pbar = QProgressBar()
                        pbar.setRange(0, 100)
                        pbar.setValue(int(min(ratio, 100)))
                        pbar.setTextVisible(False)
                        pbar.setFixedHeight(8)
                        
                        # Renk İçin Özel Stil
                        color = "#10B981" # Green
                        if ratio > 70: color = "#F59E0B" # Orange
                        if ratio > 90: color = "#EF4444" # Red
                        
                        pbar_style = f"""
                            QProgressBar {{
                                border: none;
                                background-color: #E5E7EB;
                                border-radius: 4px;
                            }}
                            QProgressBar::chunk {{
                                background-color: {color};
                                border-radius: 4px;
                            }}
                        """
                        pbar.setStyleSheet(pbar_style)
                        
                        row_layout.addLayout(header_layout)
                        row_layout.addWidget(pbar)
                        
                        self.budget_content_layout.addWidget(row_widget)
                
            except Exception as e:
                # düzeni temizler ve hatayı gösterir
                while self.budget_content_layout.count():
                    child = self.budget_content_layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()
                self.budget_content_layout.addWidget(QLabel(f"Veri hatası: {e}"))

            # B) Gecikmiş Ödemeler
            try:
                today_str = QDate.currentDate().toString("yyyy-MM-dd")
                # Gecikmiş: Vade Tarihi < Bugün VE Durum != 1 (Ödendi)
                overdue_count = self.db.cursor.execute("SELECT COUNT(*) FROM invoices WHERE due_date < ? AND status_id != 1", (today_str,)).fetchone()[0]
                
                # Yaklaşan: Sonraki 7 gün içinde Vade Tarihi
                next_week = QDate.currentDate().addDays(7).toString("yyyy-MM-dd")
                upcoming_count = self.db.cursor.execute("SELECT COUNT(*) FROM invoices WHERE due_date >= ? AND due_date <= ? AND status_id != 1", (today_str, next_week)).fetchone()[0]
                
                msg = "<html><body>"
                if overdue_count > 0:
                    msg += f"<span style='color:#EF4444; font-weight:bold;'>⚠️ {overdue_count} adet vadesi geçmiş ödeme var!</span><br>"
                else:
                    msg += "<span style='color:#10B981; font-weight:bold;'>✅ Vadesi geçen ödeme yok.</span><br>"
                    
                if upcoming_count > 0:
                    msg += f"<span style='color:#F59E0B;'>Info: Bu hafta {upcoming_count} ödeme planlanıyor.</span>"
                else:
                    msg += "<span style='color:gray;'>Bu hafta planlanan ödeme yok.</span>"
                
                msg += "</body></html>"
                self.lbl_overdue_info.setText(msg)
                
            except Exception as e:
                self.lbl_overdue_info.setText(f"Veri hatası: {e}")
            
            # Son Etkinlik (Son 5 Sipariş) - Orijinal Para Birimini Göster
            recent_orders = self.db.cursor.execute("""
                SELECT po.order_id, s.company_name, (off.price * pr.quantity) as total, c.symbol
                FROM purchase_orders po
                JOIN offers off ON po.offer_id = off.offer_id
                JOIN suppliers s ON off.supplier_id = s.supplier_id
                JOIN purchase_requests pr ON off.request_id = pr.request_id
                JOIN currencies c ON off.currency_id = c.currency_id
                ORDER BY po.order_id DESC
                LIMIT 5
            """).fetchall()
            
            self.tbl_recent.setRowCount(0)
            for r_idx, row in enumerate(recent_orders):
                self.tbl_recent.insertRow(r_idx)
                
                # ID
                self.tbl_recent.setItem(r_idx, 0, QTableWidgetItem(f"#{row[0]}"))
                # Supplier
                self.tbl_recent.setItem(r_idx, 1, QTableWidgetItem(str(row[1])))
                # Tutar (Orijinal Para Birimi)
                symbol = row[3] if row[3] else ""
                item_amt = QTableWidgetItem(f"{row[2]:,.2f} {symbol}")
                item_amt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tbl_recent.setItem(r_idx, 2, item_amt)
            
            # Charts Data (Update Monthly to use converted TRY)
            status_data = self.db.cursor.execute("""
                SELECT st.status_name, COUNT(*) 
                FROM purchase_orders po
                JOIN order_statuses st ON po.status_id = st.status_id
                GROUP BY st.status_name
            """).fetchall()
            
            # Grafik Verileri (Dönüştürülmüş TRY kullanmak için Aylık Veriyi Güncelle)
            # Aylık Verinin doğru dönüştürme için Python'da hesaplanması gerekir
            # Veya kurları geçersek karmaşık bir SQL sorgusu yapabiliriz, ancak Python burada daha kolay
            # Grafik Verileri (Aylık)
            # Saklanan exchange_rate kullan
            raw_monthly = self.db.cursor.execute("""
                SELECT strftime('%Y-%m', po.delivery_date) as month, SUM(off.price * pr.quantity * po.exchange_rate)
                FROM purchase_orders po
                JOIN offers off ON po.offer_id = off.offer_id
                JOIN purchase_requests pr ON off.request_id = pr.request_id
                WHERE po.delivery_date >= date('now', '-6 months')
                GROUP BY month
                ORDER BY month ASC
            """).fetchall()
            
            bar_data = []
            for m, total in raw_monthly:
                bar_data.append((m, total))

            self.chart_data_status = status_data
            self.chart_data_monthly = bar_data
            
            self.refresh_charts()

        except Exception as e:
            print(f"Stats Error: {e}")
        finally:
            self.db.disconnect()

    def refresh_charts(self):
        if not hasattr(self, 'chart_data_status'): return
        
        # Pasta Grafiği -> Halka Grafik
        self.pie_ax.clear()
        if self.chart_data_status:
            labels = [x[0] for x in self.chart_data_status]
            sizes = [x[1] for x in self.chart_data_status]
            total = sum(sizes)
            
            # Lejant için yüzdeleri hesapla
            legend_labels = []
            for l, s in zip(labels, sizes):
                perc = (s / total) * 100 if total > 0 else 0
                legend_labels.append(f"{l} (%{perc:.1f})")

            colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#6366F1']
            
            # Metin rengini dinamik olarak al
            try:
                style = self.lbl_title.styleSheet()
                text_color = style.split('color: ')[1].split(';')[0]
            except:
                text_color = '#111827'
                
            # Patlama efekti
            explode = [0.05] * len(sizes) 
            
            # Pasta (Halka) Çiz - Etiket yok, Yüzde yok
            edge_color = getattr(self, 'pie_edge_color', 'white')
            wedges, texts = self.pie_ax.pie(sizes, labels=None, autopct=None, 
                                            startangle=90, colors=colors, 
                                            explode=explode, shadow=False,
                                            wedgeprops=dict(width=0.4, edgecolor=edge_color))
            
            # Add Legend at the BOTTOM
            # Lejantı ALTTA Ekle
            leg = self.pie_ax.legend(wedges, legend_labels, title="Durumlar", 
                               loc="lower center", 
                               bbox_to_anchor=(0.5, -0.35), # Push down further
                               fontsize=8, ncol=2, frameon=False) # 2 columns
            
            # Lejant Metin Rengini Düzelt (Karanlık Mod için)
            leg.get_title().set_color(text_color)
            for text in leg.get_texts():
                text.set_color(text_color)

            # Merkez metni ekle (Toplam)
            self.pie_ax.text(0, 0, f"{total}\nSipariş", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)
            
        # Grafik boyutunu maksimize etmek için kenar boşluklarını ayarla, lejant için altta boşluk bırak
        self.pie_canvas.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)
        self.pie_canvas.draw()

        # Çubuk Grafik -> Izgaralı Modern Çubuk
        self.bar_ax.clear()
        if self.chart_data_monthly:
            months = [x[0] for x in self.chart_data_monthly]
            vals = [x[1] for x in self.chart_data_monthly]
            
            # Çubukların arkasına ızgara ekle
            self.bar_ax.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)
            
            bars = self.bar_ax.bar(months, vals, color='#8B5CF6', zorder=3, width=0.6)
            
            # Başlık yukarıdaki QLabel'a taşındı
            
            self.bar_ax.tick_params(axis='x', rotation=45, labelsize=9)
            self.bar_ax.tick_params(axis='y', labelsize=9)
            
            # Y ekseni için Özel Formatlayıcı (K, M, B)
            from matplotlib.ticker import FuncFormatter
            def currency_fmt(x, pos):
                if x >= 1_000_000_000:
                    return f'{x*1e-9:.1f}B'
                elif x >= 1_000_000:
                    return f'{x*1e-6:.1f}M'
                elif x >= 1_000:
                    return f'{x*1e-3:.0f}K'
                return f'{x:.0f}'

            self.bar_ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
            
            # Omurgaları (çerçeve çizgilerini) kaldır
            self.bar_ax.spines['top'].set_visible(False)
            self.bar_ax.spines['right'].set_visible(False)
            self.bar_ax.spines['left'].set_visible(False)            # Sol omurgayı da kaldır, ızgaraya güven
            self.bar_ax.spines['bottom'].set_color('#9CA3AF') # Daha yumuşak alt çizgi

        self.bar_canvas.figure.tight_layout()
        self.bar_canvas.draw()
