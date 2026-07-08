from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, 
                             QSpacerItem, QSizePolicy, QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QIcon

# Sayfa Importları
from forms.frm_dashboard import PageDashboard
from forms.frm_sas_tum import PageSASTum
from forms.frm_sas_acik import PageSASAcik
from forms.frm_sat_tum import PageSATTum
from forms.frm_sat_acik import PageSATAcik

from forms.frm_tedarikci_teklif import PageTedarikciTeklif
from forms.frm_tedarikci_detay import PageTedarikciDetay
from forms.frm_raporlar import PageRaporlar
from forms.frm_raporlar import PageRaporlar
from forms.frm_notification_popup import NotificationPopup
from forms.frm_admin import PageAdmin
from forms.frm_faturalar import PageInvoices
from forms.frm_odemeler import PagePayments

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Satın Alma Yönetim Bilgi Sistemi")
        self.resize(1200, 800)

        # Ana Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.menu_buttons = {} # Menü butonlarını saklamak için

        # ==========================================================
        # 1. BAŞLIK (ÜST KISIM)
        # ==========================================================        # ==========================================================
        self.header_frame = QFrame()
        self.header_frame.setObjectName("Header")
        self.header_frame.setFixedHeight(60)
        
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo / Başlık
        self.lbl_logo = QLabel("Satın Alma Paneli")
        self.lbl_logo.setObjectName("LogoText")
        self.header_layout.addWidget(self.lbl_logo)

        self.header_layout.addStretch()

        # Ekstra İkon 2 (Tıklanabilir - Mesaj)
        # Posta İkonu (En solda)
        self.btn_extra_2 = QPushButton("✉️") 
        self.btn_extra_2.setFixedSize(35, 35)
        self.btn_extra_2.setIconSize(QSize(24, 24))
        self.btn_extra_2.setObjectName("ExtraBtn2")
        self.btn_extra_2.setCursor(Qt.CursorShape.PointingHandCursor)
        # self.btn_extra_2.setStyleSheet(...) -> apply_styles'a taşındı
        self.header_layout.addWidget(self.btn_extra_2)

        # Bildirim Penceresi (Parent=self veriyoruz ama popup içinde None geçiyor olabilir,
        # ancak mantıken bu class içinde instance tutmamız yeterli)
        self.notification_popup = NotificationPopup(self)

        # 2. Bildirim İkonu
        self.btn_extra = QPushButton("🔔")
        self.btn_extra.setFixedSize(35, 35)
        self.btn_extra.setIconSize(QSize(32, 32))
        self.btn_extra.setIcon(QIcon()) # Placeholder
        self.btn_extra.setObjectName("ExtraBtn")
        self.btn_extra.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extra.clicked.connect(self.toggle_notifications) # Pop-up aç/kapa
        self.header_layout.addWidget(self.btn_extra)



        # Profil İkonu
        self.btn_profile = QPushButton()
        self.btn_profile.setFixedSize(37, 37)
        self.btn_profile.setIconSize(QSize(37, 37))
        self.btn_profile.setObjectName("ProfileBtn")
        self.header_layout.addWidget(self.btn_profile)

        # Kullanıcı Adı
        self.lbl_user_name = QLabel("Admin")
        self.lbl_user_name.setObjectName("UserNameResult")
        # apply_styles ile tema değişikliğine izin vermek için satır içi stil kaldırıldı
        # self.lbl_user_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e; margin-left: 10px;")
        self.header_layout.addWidget(self.lbl_user_name)

        self.main_layout.addWidget(self.header_frame)

        # ==========================================================
        # 2. GÖVDE (KENAR ÇUBUĞU + İÇERİK)
        # ==========================================================
        self.body_frame = QWidget()
        self.body_layout = QHBoxLayout(self.body_frame)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        # --- SOL MENÜ (KENAR ÇUBUĞU) ---
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("Sidebar")
        self.sidebar_frame.setFixedWidth(250)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 20)
        self.sidebar_layout.setSpacing(5)

        # >>> MENÜ 1: Satın Alma Modülü (SAT & SAS) <<<
        self.create_nested_dropdown_menu("Satın Alma Modülü", {
            "SAT (Satın Alma Talepleri)": ["Tüm Talepler", "Açık Talepler"],
            "SAS (Satın Alma Siparişleri)": ["Tüm Siparişler", "Açık Siparişler"]
        })

        # >>> MENÜ 2: TEDARİKÇİ (Açılır Menü) <<<
        self.create_dropdown_menu("Tedarikçi Modülü", ["Teklifler", "Tedarikçi Detay"])

        # >>> MENÜ 3: FİNANS (Yeni) <<<
        self.create_dropdown_menu("Finans Modülü", ["Faturalar", "Ödemeler"])

        # >>> MENÜ 3: RAPORLAR (Normal Düğme) <<<
        self.btn_rapor = QPushButton("  Raporlama Modülü")
        self.btn_rapor.setObjectName("MenuButton")
        self.btn_rapor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_layout.addWidget(self.btn_rapor)

        # >>> MENÜ 4: YÖNETİCİ PANELİ <<<
        self.btn_admin = QPushButton("  Admin Modülü")
        self.btn_admin.setObjectName("MenuButton")
        self.btn_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_layout.addWidget(self.btn_admin)

        # Spacer
        self.sidebar_layout.addStretch()
        
        # Alt Bilgi (Alt Kısım)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 0, 20, 0) # Sol ve sağ boşluk (Menülerle hizalı)

        # Versiyon (Sola Dayalı)
        self.lbl_version = QLabel("v2.35.48")
        self.lbl_version.setObjectName("VersionLabel")
        # Satır içi stil kaldırıldı, apply_styles'a taşındı
        footer_layout.addWidget(self.lbl_version)

        footer_layout.addStretch()

        # Tema Değiştirme Düğmesi (Ay/Güneş)
        self.is_dark_mode = False
        self.btn_theme = QPushButton("☀️")
        self.btn_theme.setObjectName("ThemeBtn")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedSize(35, 35)
        self.btn_theme.setIconSize(QSize(24, 24))
        self.btn_theme.setIconSize(QSize(24, 24))
        # self.btn_theme.setStyleSheet(...) -> apply_styles'a taşındı
        self.btn_theme.clicked.connect(self.toggle_theme)
        footer_layout.addWidget(self.btn_theme)

        # Çıkış Düğmesi (Sağa Dayalı)
        self.btn_exit = QPushButton("🚪") # Yer Tutucu İkon (Kullanıcı değiştirecek)
        self.btn_exit.setObjectName("ExitButton")
        self.btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_exit.setFixedSize(35, 35)
        self.btn_exit.setIconSize(QSize(24, 24))
        self.btn_exit.setIconSize(QSize(24, 24))
        # self.btn_exit.setStyleSheet(...) -> apply_styles'a taşındı
        self.btn_exit.clicked.connect(self.close) # Pencereyi kapatır
        footer_layout.addWidget(self.btn_exit)

        self.sidebar_layout.addLayout(footer_layout)

        self.body_layout.addWidget(self.sidebar_frame)

        # --- SAĞ İÇERİK ---
        # --- SAĞ İÇERİK (CONTENT) ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("Content")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0) # Kenar boşluklarını sıfırla

        # Yığın Widget (Sayfaların Değişeceği Alan)
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        # Sayfaları Oluştur ve Yığına Ekle
        self.page_dashboard = PageDashboard()
        self.page_sas_tum = PageSASTum()
        self.page_sas_acik = PageSASAcik()
        self.page_sat_tum = PageSATTum()
        self.page_sat_acik = PageSATAcik()
        self.page_tedarikci_teklif = PageTedarikciTeklif()
        self.page_tedarikci_detay = PageTedarikciDetay()
        self.page_raporlar = PageRaporlar()

        # Sırayla ekle (indeks 0, 1, 2... diye gider)
        self.stacked_widget.addWidget(self.page_dashboard)       # Index 0
        self.stacked_widget.addWidget(self.page_sas_tum)         # Index 1
        self.stacked_widget.addWidget(self.page_sas_acik)        # Index 2
        self.stacked_widget.addWidget(self.page_sat_tum)         # Index 3
        self.stacked_widget.addWidget(self.page_sat_acik)        # Index 4
        self.stacked_widget.addWidget(self.page_tedarikci_teklif)# Index 5
        self.stacked_widget.addWidget(self.page_tedarikci_detay) # Index 6
        self.stacked_widget.addWidget(self.page_raporlar)        # Index 7
        
        self.page_admin = PageAdmin()
        self.stacked_widget.addWidget(self.page_admin)           # Index 8

        self.page_invoices = PageInvoices()
        self.page_payments = PagePayments()
        self.stacked_widget.addWidget(self.page_invoices)        # Index 9
        self.stacked_widget.addWidget(self.page_payments)        # Index 10


        # Başlangıçta Gösterge Paneli Açık Olsun
        self.stacked_widget.setCurrentIndex(0)

        # ==========================================================
        # SAYFA YÖNLENDİRMELERİ
        # ==========================================================
        
        # 1. Gösterge Paneline Dönüş (Logo veya Posta İkonu)
        self.btn_extra_2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # 2. Raporlar Düğmesi
        self.btn_rapor.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(7))
        self.btn_admin.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(8))

        # 3. Alt Menü Düğmeleri Bağlantıları
        
        # SAS
        if "Tüm Siparişler" in self.menu_buttons:
            self.menu_buttons["Tüm Siparişler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        if "Açık Siparişler" in self.menu_buttons:
            self.menu_buttons["Açık Siparişler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # SAT
        if "Tüm Talepler" in self.menu_buttons:
            self.menu_buttons["Tüm Talepler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        if "Açık Talepler" in self.menu_buttons:
            self.menu_buttons["Açık Talepler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        # Tedarikçi
        if "Teklifler" in self.menu_buttons:
            self.menu_buttons["Teklifler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        if "Tedarikçi Detay" in self.menu_buttons:
            self.menu_buttons["Tedarikçi Detay"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(6))

        # Finans
        if "Faturalar" in self.menu_buttons:
            self.menu_buttons["Faturalar"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(9))
        if "Ödemeler" in self.menu_buttons:
            self.menu_buttons["Ödemeler"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(10))

        self.body_layout.addWidget(self.content_frame)
        self.main_layout.addWidget(self.body_frame)

        self.apply_styles()


    def toggle_notifications(self):
        if self.notification_popup.isVisible():
            self.notification_popup.hide()
        else:
            # 1. Düğmenin ana pencereye (self) göre konumunu alıyoruz.
            # mapToGlobal DEĞİL, mapTo(self) kullanıyoruz.
            # Böylece pencere nereye giderse gitsin, açılır pencere düğmenin yanında kalır.
            btn_pos_local = self.btn_extra.mapTo(self, QPoint(0, 0))
            
            # 2. X Hesabı:
            x = btn_pos_local.x() + self.btn_extra.width() - self.notification_popup.width() + 10
            
            # 3. Y Hesabı:
            y = btn_pos_local.y() + self.btn_extra.height() + 5
            
            self.notification_popup.move(x, y)
            self.notification_popup.raise_() # En öne getir (Katman)
            self.notification_popup.show()
    
    def create_nested_dropdown_menu(self, title, groups_dict):
        """
        groups_dict format: {"Group Title": ["Item 1", "Item 2"], ...}
        """
        # 1. Ana Başlık Düğmesi
        btn_main = QPushButton(f"  {title} ▼") 
        btn_main.setObjectName("MenuButton")
        btn_main.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_layout.addWidget(btn_main)

        # 2. Alt Menü Konteyneri
        sub_menu_frame = QFrame()
        sub_menu_frame.setObjectName("SubMenuFrame")
        sub_menu_frame.setVisible(False)
        
        sub_layout = QVBoxLayout(sub_menu_frame)
        sub_layout.setContentsMargins(0, 5, 0, 5)
        sub_layout.setSpacing(2)

        for group_title, items in groups_dict.items():
            # Grup Başlığı (Etiket benzeri düğme ama devre dışı veya sadece farklı stil)
            lbl_group = QLabel(f"  {group_title}")
            lbl_group.setObjectName("MenuHeader") 
            sub_layout.addWidget(lbl_group)
            
            for item_name in items:
                # İç içe öğeler için ekstra girinti
                btn_sub = QPushButton(f"      • {item_name}") 
                btn_sub.setObjectName("SubMenuButton")
                btn_sub.setCursor(Qt.CursorShape.PointingHandCursor)
                sub_layout.addWidget(btn_sub)
                
                # Düğmeyi sözlüğe kaydet
                self.menu_buttons[item_name] = btn_sub

        self.sidebar_layout.addWidget(sub_menu_frame)

        # 3. Tıklama Olayı
        btn_main.clicked.connect(lambda: self.toggle_menu(sub_menu_frame, btn_main))

    def create_dropdown_menu(self, title, sub_items):
        # 1. Ana Başlık Düğmesi
        btn_main = QPushButton(f"  {title} ▼") 
        btn_main.setObjectName("MenuButton")
        btn_main.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_layout.addWidget(btn_main)

        # 2. Alt Menü Konteyneri
        sub_menu_frame = QFrame()
        sub_menu_frame.setObjectName("SubMenuFrame")
        sub_menu_frame.setVisible(False)
        
        sub_layout = QVBoxLayout(sub_menu_frame)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.setSpacing(0)

        for item_name in sub_items:
            btn_sub = QPushButton(f"    • {item_name}") 
            btn_sub.setObjectName("SubMenuButton")
            btn_sub.setCursor(Qt.CursorShape.PointingHandCursor)
            sub_layout.addWidget(btn_sub)
            
            # Düğmeyi sözlüğe kaydet
            self.menu_buttons[item_name] = btn_sub

        self.sidebar_layout.addWidget(sub_menu_frame)

        # 3. Tıklama Olayı
        btn_main.clicked.connect(lambda: self.toggle_menu(sub_menu_frame, btn_main))

    def toggle_menu(self, frame, btn):
        is_visible = frame.isVisible()
        frame.setVisible(not is_visible)
        
        current_text = btn.text()
        if not is_visible:
            btn.setText(current_text.replace("▼", "▲"))
        else:
            btn.setText(current_text.replace("▲", "▼"))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_styles()

    def update_icons(self):
        # =========================================================================
        # İKON AYARLARI (PNG RESİMLERİNİZ İÇİN)
        # =========================================================================
        # Buraya kendi .png dosyalarınızın tam yolunu veya proje klasöründeki adını yazın.
        # Örnek: icon_mail = "/Users/hasan/Desktop/mail.png" veya ":/resources/mail.png"
        
        if self.is_dark_mode:
            # --- KOYU TEMA İKONLARI ---
            # Arka plan koyu olduğu için AÇIK RENKLİ iconlar tercih edin.
            icon_mail = ":/resources/main_page_dark.png"      # Örn: "icons/mail_white.png"
            icon_bell = ":/resources/notification_dark.png"      # Örn: "icons/bell_white.png"
            icon_profile = ":/resources/user_dark.png"   # Örn: "icons/user_white.png"
            icon_theme = ":/resources/theme_dark.png"     # Örn: "icons/sun.png" (Light moda geçiş butonu)
            icon_exit = ":/resources/exit_light.png"      # Örn: "icons/logout_white.png"
            
        else:
            # --- AÇIK TEMA İKONLARI ---
            # Arka plan açık olduğu için KOYU RENKLİ iconlar tercih edin.
            icon_mail = ":/resources/main_page_light.PNG"      # Örn: "icons/mail_black.png"
            icon_bell = ":/resources/notification_light.png"      # Örn: "icons/bell_black.png"
            icon_profile = ":/resources/user_light.png"   # Örn: "icons/user_black.png"
            icon_theme = ":/resources/theme_light.png"     # Örn: "icons/moon.png" (Dark moda geçiş butonu)
            icon_exit = ":/resources/exit_light.png"      # Örn: "icons/logout_black.png"

        # --- İKONLARI GÜNCELLEME MANTIĞI ---
        # Eğer yukarıya dosya yolu ("") yazdıysanız o resmi kullanır.
        # Boş bıraktıysanız ("") emojiyi kullanmaya devam eder.

        # 1. Mail İkonu
        if icon_mail: 
            self.btn_extra_2.setIcon(QIcon(icon_mail))
            self.btn_extra_2.setText("") 
        else: 
            self.btn_extra_2.setIcon(QIcon()) 
            self.btn_extra_2.setText(txt_mail)

        # 2. Bildirim İkonu
        if icon_bell: 
            self.btn_extra.setIcon(QIcon(icon_bell))
            self.btn_extra.setText("") 
        else: 
            self.btn_extra.setIcon(QIcon()) 
            self.btn_extra.setText(txt_bell)

        # 3. Profil İkonu
        if icon_profile: 
            self.btn_profile.setIcon(QIcon(icon_profile))
            # Profil düğmesi metin içermiyor, sadece ikon.
        
        # 4. Tema Butonu
        if icon_theme: 
            self.btn_theme.setIcon(QIcon(icon_theme))
            self.btn_theme.setText("") 
        else: 
            self.btn_theme.setIcon(QIcon()) 
            self.btn_theme.setText(txt_theme)
            
        # 5. Çıkış Butonu
        if icon_exit: 
            self.btn_exit.setIcon(QIcon(icon_exit))
            self.btn_exit.setText("") 
        else: 
            self.btn_exit.setIcon(QIcon()) 
            self.btn_exit.setText(txt_exit)

    def apply_styles(self):
        # Tema değiştiğinde ikonları da güncelle
        self.update_icons()
        
        if self.is_dark_mode:
            # --- DARK THEME ---
            bg_color = "#2c3e50"
            sidebar_bg = "#1a252f"
            header_bg = "#2c3e50"
            text_color = "#FFFFFF"
            content_bg = "#34495e"
            border_color = "#455a64"
            menu_hover = "#34495e"
            sub_menu_bg = "#253340" # Lighter than sidebar (#1a252f)
            sub_menu_text = "#FFFFFF"   # White text
            logo_color = "#ecf0f1"
            hover_bg = "rgba(255, 255, 255, 0.1)"
            
            # Menü Başlığı (Alt Grup)
            menu_header_bg = "#1B2631" # A bit darker than sub-menu
            menu_header_text = "#60A5FA" # Blue accent
            
            # Oklar (SVG)
            arrow_down = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik02IDlsNiA2IDYtNiIvPjwvc3ZnPg=="
            arrow_right = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik05IDZsNiA2LTYgNiIvPjwvc3ZnPg=="
            arrow_left = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNSA2bC02IDYgNiA2Ii8+PC9zdmc+"
            
        else:
            # --- LIGHT THEME ---
            bg_color = "#f5f6fa"
            sidebar_bg = "#5a6e82"
            header_bg = "#ffffff"
            text_color = "#2c3e50"
            content_bg = "#ecf0f1"
            border_color = "#dcdde1"
            menu_hover = "#34495e"
            sub_menu_bg = "#6c8096" # Lighter than sidebar (#5a6e82)
            sub_menu_text = "#FFFFFF"   # White text
            logo_color = "#2c3e50"
            hover_bg = "rgba(0, 0, 0, 0.15)"
            
            # Menu Header (Sub-Group)
            menu_header_bg = "#546E7A" # Darker Slate
            menu_header_text = "#FFFFFF"

            # Arrows (SVG)
            arrow_down = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMjc0MTUxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTYgOWw2IDYgNi02Ii8+PC9zdmc+"
            arrow_right = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMjc0MTUxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTkgNmw2IDYtNiA2Ii8+PC9zdmc+"
            arrow_left = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMjc0MTUxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTE1IDZsLTYgNiA2IDYiLz48L3N2Zz4="

        style_sheet = f"""
        /* GENEL OKLAR */
        QComboBox::down-arrow {{
            image: url({arrow_down});
            width: 12px;
            height: 12px;
        }}
        QTabBar QToolButton::right-arrow {{
            image: url({arrow_right});
            width: 12px;
            height: 12px;
        }}
        QTabBar QToolButton::left-arrow {{
            image: url({arrow_left});
            width: 12px;
            height: 12px;
        }}
        
        /* GENEL */
        QMainWindow {{ background-color: {bg_color}; }}
        QWidget {{ font-family: 'Segoe UI', sans-serif; }}

        /* HEADER */
        QFrame#Header {{ background-color: {header_bg}; border-bottom: 1px solid {border_color}; }}
        QLabel#LogoText {{ font-size: 20px; font-weight: bold; color: {logo_color}; }}
        
        /* BAŞLIK İKON DÜĞMELERİ */
        QPushButton#ExtraBtn, QPushButton#ExtraBtn2, QPushButton#ProfileBtn, QPushButton#ThemeBtn, QPushButton#ExitButton {{
            background-color: transparent; 
            border: none;
            border-radius: 5px;
            color: {text_color}; /* Default text color for icons */
            font-weight: bold;
            font-size: 16px;
        }}
        /* Çıkış Düğmesi Özel Rengi (Kırmızı) */
        QPushButton#ExitButton {{
            color: #e74c3c;
        }}

        QPushButton#ExtraBtn:hover, QPushButton#ExtraBtn2:hover, QPushButton#ThemeBtn:hover, QPushButton#ExitButton:hover {{
            background-color: {hover_bg};
        }}

        QLabel#UserNameResult {{ font-size: 14px; font-weight: bold; color: {text_color}; margin-left: 10px; }}

        /* KENAR ÇUBUĞU */
        QFrame#Sidebar {{ background-color: {sidebar_bg}; }}
        
        /* ALT BİLGİ ETİKETLERİ */
        QLabel {{ color: {text_color}; }} 
        QLabel#VersionLabel {{ color: #FFFFFF; font-size: 12px; }} /* Açıkça Beyaz */ 

        /* ANA MENÜ DÜĞMELERİ */
        QPushButton#MenuButton {{
            background-color: transparent;
            color: #ecf0f1;
            text-align: left;
            padding: 15px 20px;
            border: none;
            font-size: 15px;
            font-weight: 600;
        }}
        QPushButton#MenuButton:hover {{
            background-color: {menu_hover};
            border-left: 4px solid #3498db;
        }}

        /* ALT MENÜ ALANI */
        QFrame#SubMenuFrame {{
            background-color: {sub_menu_bg}; 
        }}
        
        /* MENÜ BAŞLIĞI (GRUP BAŞLIĞI) */
        QLabel#MenuHeader {{
            background-color: {menu_header_bg};
            color: {menu_header_text};
            font-weight: 800; /* Extra Bold */
            font-size: 11px;
            padding: 6px 10px;
            margin-top: 8px;
            margin-bottom: 2px;
            border-left: 3px solid {menu_header_text}; /* Vurgu kenarlığı */
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}

        /* ALT MENÜ DÜĞMELERİ */
        QPushButton#SubMenuButton {{
            background-color: transparent;
            color: {sub_menu_text}; 
            text-align: left;
            padding: 10px 20px;
            border: none;
            font-size: 14px;
        }}
        QPushButton#SubMenuButton:hover {{
            color: white;
            background-color: rgba(255,255,255,0.05);
        }}

        /* CONTENT */
        QFrame#Content {{ background-color: {content_bg}; }}
        
        /* AÇILIR KUTU & TARİH EDİTÖRÜ BİRLEŞTİRME */
        QComboBox, QDateEdit {{
            background-color: {bg_color}; 
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 5px;
            color: {text_color};
        }}
        /* varsayılanı kullanmak için ok stili kaldırıldı */
        QComboBox QAbstractItemView {{
            background-color: {bg_color};
            color: {text_color};
            selection-background-color: #2563EB;
            selection-color: white;
            border: 1px solid {border_color};
        }}
        """
        # 12. Notification Popup Tema Güncellemesi
        if hasattr(self, 'notification_popup'):
            self.notification_popup.update_theme(self.is_dark_mode)

        # 13. Gösterge Paneli Tema Güncellemesi
        # 13. Dashboard Tema Güncellemesi
        if hasattr(self, 'page_dashboard'):
            self.page_dashboard.update_theme(self.is_dark_mode)

        # 14. SAS Tüm Siparişler
        if hasattr(self, 'page_sas_tum'):
            self.page_sas_tum.update_theme(self.is_dark_mode)

        # 15. SAS Açık Siparişler
        if hasattr(self, 'page_sas_acik'):
            self.page_sas_acik.update_theme(self.is_dark_mode)

        # 16. SAT Tüm
        if hasattr(self, 'page_sat_tum'):
            self.page_sat_tum.update_theme(self.is_dark_mode)

        # 17. SAT Açık
        if hasattr(self, 'page_sat_acik'):
            self.page_sat_acik.update_theme(self.is_dark_mode)
            
        # 18. Tedarikçi Teklif
        if hasattr(self, 'page_tedarikci_teklif'):
            self.page_tedarikci_teklif.update_theme(self.is_dark_mode)

        # 19. Tedarikçi Detay
        if hasattr(self, 'page_tedarikci_detay'):
            self.page_tedarikci_detay.update_theme(self.is_dark_mode)
            
        # 20. Raporlar
        if hasattr(self, 'page_raporlar'):
            self.page_raporlar.update_theme(self.is_dark_mode)

        if hasattr(self, 'page_admin'):
            self.page_admin.update_theme(self.is_dark_mode)

        # Finans Teması
        if hasattr(self, 'page_invoices'):
            self.page_invoices.update_theme(self.is_dark_mode)
        if hasattr(self, 'page_payments'):
            self.page_payments.update_theme(self.is_dark_mode)

        self.setStyleSheet(style_sheet)
