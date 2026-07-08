from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QHBoxLayout, QMessageBox, QFileDialog, QFrame)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.custom_dialogs import CustomDialogs
from utils.theme_helper import ThemeHelper
from utils.currency_fetcher import CurrencyFetcher
import pandas as pd

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import numpy as np
try:
    from sklearn.linear_model import LinearRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class PageRaporlar(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.lbl_title = QLabel("Detaylı Raporlar")
        self.lbl_title.setObjectName("PageTitle")
        self.layout.addWidget(self.lbl_title)

        # KONTROL PANELİ (Kart Stili)
        control_frame = QFrame()
        control_frame.setObjectName("ControlFrame")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(20, 15, 20, 15)
        control_layout.setSpacing(15)

        self.cmb_report_type = QComboBox()
        self.cmb_report_type.addItems([
            "-- Rapor Seçiniz --", 
            "Tedarikçi Bazlı Harcama", 
            "Ürün Bazlı Harcama", 
            "Aylık Harcama", 
            "Personel Bazlı Harcama", 
            "Kategori Bazlı Harcama",
            "Tedarikçi Ekstresi",
            "Aylık Gider Raporu",
            "Kur Farkı / Risk Analizi"
        ])
        self.cmb_report_type.setMinimumWidth(250)
        
        self.btn_run = QPushButton("Raporu Görüntüle")
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.clicked.connect(self.run_report)
        
        self.btn_export = QPushButton("Excel'e Aktar")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_excel)
        
        control_layout.addWidget(QLabel("Rapor Türü:"))
        control_layout.addWidget(self.cmb_report_type)
        control_layout.addWidget(self.btn_run)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_export)
        
        self.layout.addWidget(control_frame)

        # İÇERİK ALANI
        # Grafik üstte (daha küçük) ve Tablo altta olacak şekilde düzenleniyor.
        
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(self.canvas)

        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table)
        
    def update_theme(self, is_dark):
        self.is_dark = is_dark
        bg_color = "#1F2937" if is_dark else "#FFFFFF"
        text_color = "#E5E7EB" if is_dark else "#111827"
        
        # Grafik Teması

        colors = ThemeHelper.get_chart_colors(is_dark)
        
        self.canvas.figure.patch.set_facecolor(colors['facecolor'])
        self.ax.set_facecolor(colors['facecolor'])
        self.ax.title.set_color(colors['text'])
        self.ax.xaxis.label.set_color(colors['text'])
        self.ax.yaxis.label.set_color(colors['text'])
        self.ax.tick_params(colors=colors['text'])
        for spine in self.ax.spines.values():
            spine.set_edgecolor(colors['edge'])
        self.canvas.draw()

        if is_dark:
            self.lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E5E7EB;")
            
            self.findChild(QFrame, "ControlFrame").setStyleSheet("background-color: #374151; border-radius: 10px;")
            self.cmb_report_type.setStyleSheet("padding: 5px; background-color: #1F2937; color: #F9FAFB; border: 1px solid #4B5563; border-radius: 6px;")
            
            self.btn_run.setStyleSheet("QPushButton { background-color: #2563EB; color: white; padding: 6px 15px; border-radius: 6px; font-weight: bold; border: none;} QPushButton:hover { background-color: #1D4ED8; }")
            self.btn_export.setStyleSheet("QPushButton { background-color: #059669; color: white; padding: 6px 15px; border-radius: 6px; font-weight: bold; border: none;} QPushButton:hover { background-color: #047857; }")
            
            self.table.setStyleSheet("""
                QTableWidget { 
                    background-color: #111827; 
                    alternate-background-color: #1F2937;
                    color: #E5E7EB; 
                    border: none; 
                    gridline-color: #374151; 
                }
                QHeaderView { background-color: #111827; }
                QHeaderView::section { 
                    background-color: #1F2937; 
                    color: #9CA3AF; 
                    border: 1px solid #374151; 
                    padding: 5px; 
                    font-weight: bold; 
                }
                QTableCornerButton::section { background-color: #1F2937; border: 1px solid #374151; }
                QTableWidget::item:selected { background-color: #374151; color: #FFFFFF; }
            """)
        else:
            self.lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
            
            self.findChild(QFrame, "ControlFrame").setStyleSheet("background-color: #F3F4F6; border-radius: 10px;")
            self.cmb_report_type.setStyleSheet("padding: 5px; background-color: #FFFFFF; color: #111827; border: 1px solid #D1D5DB; border-radius: 6px;")
            
            self.btn_run.setStyleSheet("QPushButton { background-color: #3B82F6; color: white; padding: 6px 15px; border-radius: 6px; font-weight: bold; border: none;} QPushButton:hover { background-color: #2563EB; }")
            self.btn_export.setStyleSheet("QPushButton { background-color: #10B981; color: white; padding: 6px 15px; border-radius: 6px; font-weight: bold; border: none;} QPushButton:hover { background-color: #059669; }")
            
            self.table.setStyleSheet("""
                QTableWidget { background-color: #FFFFFF; color: #1F2937; border: 1px solid #E5E7EB; gridline-color: #E5E7EB; }
                QHeaderView::section { background-color: #F9FAFB; color: #4B5563; border: none; border-bottom: 2px solid #E5E7EB; padding: 5px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #E0E7FF; color: #1E3A8A; }
            """)

    def run_report(self):
        rtype = self.cmb_report_type.currentText()
        query = ""
        headers = []
        
        r_check = rtype.strip()
        if r_check == "Tedarikçi Bazlı Harcama":
            query = """
                SELECT s.company_name, po.order_id, pr.quantity, o.price, c.code
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN suppliers s ON o.supplier_id = s.supplier_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN currencies c ON o.currency_id = c.currency_id
            """
            headers = ["Tedarikçi", "Sipariş Adedi", "Toplam Tutar"]
            group_col_index = 0
            
        elif r_check == "Ürün Bazlı Harcama":
            query = """
                SELECT i.item_name, po.order_id, pr.quantity, o.price, c.code
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                JOIN currencies c ON o.currency_id = c.currency_id
            """
            headers = ["Ürün", "Toplam Miktar", "Toplam Tutar"]
            group_col_index = 0
        
        elif r_check == "Aylık Harcama":
            query = """
                SELECT strftime('%Y-%m', po.delivery_date), po.order_id, pr.quantity, o.price, c.code
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN currencies c ON o.currency_id = c.currency_id
                ORDER BY 1 ASC
            """
            headers = ["Ay", "Sipariş Sayısı", "Tutar"]
            group_col_index = 0
            
        elif r_check == "Personel Bazlı Harcama":
            query = """
                SELECT u.first_name || ' ' || COALESCE(u.last_name, ''), po.order_id, pr.quantity, o.price, c.code
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN users u ON pr.requester_user_id = u.user_id
                JOIN currencies c ON o.currency_id = c.currency_id
            """
            headers = ["Personel", "Sipariş Sayısı", "Toplam Tutar"]
            group_col_index = 0

        elif r_check == "Kategori Bazlı Harcama":
            query = """
                SELECT cat.category_name, po.order_id, pr.quantity, o.price, c.code
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN items i ON pr.item_id = i.item_id
                JOIN categories cat ON i.category_id = cat.category_id
                JOIN currencies c ON o.currency_id = c.currency_id
            """
            headers = ["Kategori", "Sipariş Sayısı", "Toplam Tutar"]
            group_col_index = 0

        elif r_check == "Tedarikçi Ekstresi":
            query = """
                SELECT i.invoice_no, i.invoice_date, s.company_name, i.total_amount, 
                       (SELECT SUM(amount) FROM payments WHERE invoice_id = i.invoice_id) as paid
                FROM invoices i
                LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
                ORDER BY s.company_name
            """
            headers = ["Tedarikçi", "Fatura Sayısı", "Toplam Fatura", "Toplam Ödenen", "Kalan Bakiye"]
            
        elif r_check == "Aylık Gider Raporu":
            query = """
                SELECT strftime('%Y-%m', i.invoice_date) as month, COUNT(i.invoice_id), SUM(i.total_amount), SUM(i.tax_amount)
                FROM invoices i
                GROUP BY month
                ORDER BY month ASC
            """
            headers = ["Ay", "Fatura Sayısı", "Toplam Tutar (KDV Dahil)", "Toplam KDV"]
            
        elif r_check == "Kur Farkı / Risk Analizi":
            query = """
                SELECT i.invoice_no, s.company_name, c.code, 
                       po.exchange_rate, i.exchange_rate,
                       (o.price * pr.quantity) as amount_fc,
                       ((o.price * pr.quantity) * i.exchange_rate) - ((o.price * pr.quantity) * po.exchange_rate) as diff_try
                FROM invoices i
                JOIN purchase_orders po ON i.order_id = po.order_id
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN suppliers s ON i.supplier_id = s.supplier_id
                JOIN currencies c ON o.currency_id = c.currency_id
                WHERE i.order_id IS NOT NULL
                ORDER BY diff_try DESC
            """
            headers = ["Fatura No", "Tedarikçi", "Döviz", "Sipariş Kuru", "Fatura Kuru", "Tutar (Döviz)", "Kur Farkı (TL)"]
            
        else:
            return

        self.db.connect()
        try:
            # 1. Fetch Rates
            rates = CurrencyFetcher.get_rates()
            # Fallback defaults
            if 'USD' not in rates: rates['USD'] = 1.0
            if 'EUR' not in rates: rates['EUR'] = 1.0

            # 2. Fetch Raw Data
            self.db.cursor.execute(query)
            raw_rows = self.db.cursor.fetchall()
            
            # 3. Python tarafında İşleme & Gruplama
            # Yapı: Anahtar -> {'count': 0, 'total': 0.0, 'quantity': 0}
            agg_data = {}
            final_rows = []
            
            if r_check in ["Tedarikçi Ekstresi", "Aylık Gider Raporu", "Kur Farkı / Risk Analizi"]:
                # Direct Row Mapping or Custom Aggregation
                
                if r_check == "Tedarikçi Ekstresi":
                     # TEDARİKÇİYE GÖRE GRUPLA
                     # Satır: fatura_no, tarih, tedarikçi, toplam, ödenen
                     agg_map = {} # Anahtar: tedarikçi_adı -> {count, total, paid}
                     
                     for row in raw_rows:
                         supp = row[2] if row[2] else "Bilinmiyor"
                         total = row[3] if row[3] else 0.0
                         paid = row[4] if row[4] else 0.0
                         
                         if supp not in agg_map:
                             agg_map[supp] = {'count': 0, 'total': 0.0, 'paid': 0.0}
                         
                         agg_map[supp]['count'] += 1
                         agg_map[supp]['total'] += total
                         agg_map[supp]['paid'] += paid
                     
                     # Listeye Dönüştür
                     for supp, data in agg_map.items():
                         # Kayan nokta hatası yaşamamak için 2 ondalığa yuvarla
                         total = round(data['total'], 2)
                         paid = round(data['paid'], 2)
                         balance = total - paid
                         
                         # Hassasiyet düzeltmesi: bakiye 0'a çok yakınsa (örn: -0.0000001) 0 yap

                         if abs(balance) < 0.01:
                             balance = 0.0
                             
                         final_rows.append([supp, data['count'], total, paid, balance])
                     
                     # Bakiyeye göre AZALAN sırala
                     final_rows.sort(key=lambda x: x[4], reverse=True)
                     
                else:
                    for row in raw_rows:
                        if r_check == "Aylık Gider Raporu":
                            # month, count, total, tax
                            m, count, total, tax = row
                            total = total if total else 0.0
                            tax = tax if tax else 0.0
                            final_rows.append([m, count, total, tax])
                            
                        elif r_check == "Kur Farkı / Risk Analizi":
                            # inv_no, comp, code, r_ord, r_inv, amt, diff
                            inv_no, comp, code, r_ord, r_inv, amt, diff = row
                            comp = comp if comp else "-"
                            r_ord = r_ord if r_ord else 1.0
                            r_inv = r_inv if r_inv else 1.0
                            amt = amt if amt else 0.0
                            diff = diff if diff else 0.0
                            final_rows.append([inv_no, comp, code, f"{r_ord:.4f}", f"{r_inv:.4f}", f"{amt:,.2f}", diff])
            else:
                # SİPARİŞLER İÇİN ESKİ GRUPLAMA MANTIĞI
                for row in raw_rows:
                    key = row[0] # Grup Anahtarı
                    # satır yapısı genelde: key, order_id, quantity, price, currency
                    qty = row[2]
                    price = row[3]
                    code = row[4]
                    
                    rate = rates.get(code, 1.0)
                    total_try = price * qty * rate
                    
                    if key not in agg_data:
                        agg_data[key] = {'count': 0, 'total': 0.0, 'quantity': 0}
                    
                    agg_data[key]['count'] += 1
                    agg_data[key]['total'] += total_try
                    agg_data[key]['quantity'] += qty

                # 4. Görüntüleme için Listeyi Düzleştir
                if rtype == "Ürün Bazlı Harcama":
                     for k, v in agg_data.items():
                        final_rows.append([k, v['quantity'], v['total']])
                else:
                     for k, v in agg_data.items():
                        final_rows.append([k, v['count'], v['total']])

                # Sırala
                if rtype == "Aylık Harcama":
                    final_rows.sort(key=lambda x: x[0]) # Ay Dizisine göre sırala
                else:
                    final_rows.sort(key=lambda x: x[2], reverse=True) # Sort by Total Amount DESC
                
                if rtype == "Kur Farkı / Risk Analizi":
                     # Sort by Diff DESC (Highest Loss First)
                     final_rows.sort(key=lambda x: x[6], reverse=True)

            rows = final_rows
            
            # YAPAY ZEKA / REGRESYON MANTIĞI
            prediction_info = None
            if rtype == "Aylık Harcama" and len(rows) >= 2 and HAS_SKLEARN:
                try:
                    # Veriyi Hazırla
                    # X = Ay İndeksi (0, 1, 2...), y = Tutar
                    X = np.arange(len(rows)).reshape(-1, 1)
                    y = np.array([r[2] for r in rows])
                    
                    # Modeli Eğit
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Trend Çizgisi Hesapla (mevcut veri için)
                    trend_values = model.predict(X)
                    
                    # Gelecek Ayı Tahmin Et
                    next_index = np.array([[len(rows)]])
                    next_value = model.predict(next_index)[0]
                    
                    # Gelecek Ay Etiketi
                    last_month_str = rows[-1][0]
                    last_date = datetime.strptime(last_month_str, "%Y-%m")
                    next_date = last_date + timedelta(days=32)
                    next_month_str = next_date.strftime("%Y-%m")
                    
                    prediction_info = {
                        'trend_values': trend_values,
                        'next_label': next_month_str + " (AI Tahmin)",
                        'next_value': next_value,
                        'slope': model.coef_[0] # Optional: to show trend direction
                    }
                except Exception as ai_err:
                    print(f"AI Error: {ai_err}")

            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(0)
            
            for r_idx, row in enumerate(rows):
                self.table.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    if isinstance(val, float):
                        txt = f"{val:,.2f}"
                    else:
                        txt = str(val)
                    item = QTableWidgetItem(txt)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)
            
            self.render_chart(rtype, rows, prediction_info)

        except Exception as e:
            CustomDialogs.error(self, str(e))
        finally:
            self.db.disconnect()

    def render_chart(self, rtype, rows, prediction_info=None):
        self.ax.clear()
        
        if not rows:
            self.canvas.draw()
            return
            
        labels = [str(r[0]) for r in rows] # Show all rows
        
        # Select data column for chart
        # Select data column for chart
        if rtype == "Aylık Gider Raporu":
            values = [r[2] for r in rows] # Total Amount (KDV Dahil)
        elif rtype == "Tedarikçi Ekstresi":
            # Rows are already aggregated: [Supplier, Count, Total, Paid, Balance]
            # Take top 10 by Balance (Index 4)
            
            # They are already sorted by balance DESC in run_report
            top_10 = rows[:10]
            labels = [x[0] for x in top_10]
            values = [x[4] for x in top_10] # Balance

            
            # Update title to be specific
            self.ax.set_title("En Yüksek Borç Bakiyesi (Top 10 Tedarikçi)", fontsize=12, fontweight='bold', pad=15)
            self.ax.set_ylabel("Kalan Bakiye (TL)")
            
            # Special return to skip standard bar chart title setting below if needed, 
            # or just let it fall through to plot.
            # We must update 'rtype' or handle title logic carefully.
            # Let's rely on standard plotting below using these new labels and values.
            
        else:
            values = [r[-1] for r in rows]
            # Verify if values are numeric
            if values and not isinstance(values[0], (int, float)):
                 # Skip charting if last column is not numeric (e.g. Status)
                 self.canvas.draw()
                 return
        
        # Soft Grid
        self.ax.grid(True, linestyle='--', alpha=0.3, zorder=0)
        
        color = '#3B82F6'

        if rtype == "Aylık Harcama":
             # Plot Actual Data (Line + Area)
             # Use integer indices for x-axis to allow filling
             x = np.arange(len(labels))
             
             self.ax.plot(x, values, marker='o', linestyle='-', color='#10B981', linewidth=3, label='Gerçekleşen', zorder=3)
             self.ax.fill_between(x, values, color='#10B981', alpha=0.1, zorder=2)
             
             self.ax.set_xticks(x)
             self.ax.set_xticklabels(labels)
             
             if prediction_info:
                 # Plot Trend Line (Regression Line on existing data)
                 trend_values = prediction_info['trend_values']
                 self.ax.plot(x, trend_values, linestyle='--', color='#6B7280', linewidth=1.5, alpha=0.8, label='Genel Eğilim', zorder=3)
                 
                 # Plot Future Prediction
                 pred_label = prediction_info['next_label']
                 pred_value = prediction_info['next_value']
                 
                 # We need to extend X axis for prediction
                 last_x = x[-1]
                 next_x = last_x + 1
                 
                 # Connect last trend point to prediction
                 # Connect last trend point to prediction (Line only)
                 self.ax.plot([last_x, next_x], [trend_values[-1], pred_value], 
                              linestyle=':', color='#F59E0B', linewidth=2, label='AI Tahmini', zorder=4)
                 
                 # Plot the Prediction Star (Single point)
                 self.ax.plot(next_x, pred_value, marker='*', markersize=14, color='#F59E0B', zorder=5)
                 
                 # Annotation with Box
                 self.ax.text(next_x, pred_value * 1.05, f"{pred_value:,.0f} TL", 
                              ha='center', fontsize=10, color='white', fontweight='bold',
                              bbox=dict(boxstyle="round,pad=0.3", fc="#F59E0B", ec="none", alpha=0.9), zorder=5)

             self.ax.set_title("Aylık Harcama Trendi", fontsize=12, fontweight='bold', pad=15)
             self.ax.set_ylabel("Tutar (TL)")
             self.ax.legend(loc='upper left', frameon=True, fancybox=True, framealpha=0.9)
             
        else:
             bars = self.ax.bar(labels[:10], values[:10], color=color, zorder=3) # Limit other charts to top 10
             
             if rtype != "Tedarikçi Ekstresi":
                 self.ax.set_title(rtype, fontsize=12, fontweight='bold', pad=15)
                 self.ax.set_ylabel("Tutar")
             
        self.ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        self.ax.tick_params(axis='y', labelsize=9)

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

        self.ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_color('#9CA3AF')
        
        self.canvas.figure.tight_layout()
        
        # Apply Theme Colors to new chart elements
        is_dark = getattr(self, 'is_dark', False)
        text_color = '#E5E7EB' if is_dark else '#111827'
        
        self.ax.title.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        self.ax.xaxis.label.set_color(text_color)
        self.ax.tick_params(colors=text_color)
        
        self.canvas.draw()

    def export_excel(self):
        if self.table.rowCount() == 0:
            CustomDialogs.warning(self, "Dışarı aktarılacak veri yok.")
            return

        # Kullanıcı 'basit' yerel pencere istedi. 
        # Not: Yerel pencereler İşletim Sistemi Dili ve Temasını takip eder, bu yüzden macOS ayarlarına bağlı olarak
        # 'Save'/'Cancel' butonları İngilizce veya farklı dilde görünebilir.
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Excel Olarak Kaydet",
            "", 
            "Excel Dosyaları (*.xlsx)"
        )

        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            
            try:
                headers = []
                for i in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(i).text())
                
                data = []
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_name, index=False)
                
                CustomDialogs.info(self, "Dosya Kaydedildi.")
                
            except Exception as e:
                CustomDialogs.error(self, str(e))
