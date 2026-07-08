from PyQt6.QtWidgets import QMessageBox
from utils.theme_helper import ThemeHelper

class CustomDialogs:
    @staticmethod
    def show_message(parent, title, message, icon_type, button_text="Tamam"):
        msg = QMessageBox(parent)
        
        is_dark = False
        if parent:
            is_dark = getattr(parent, 'is_dark', getattr(parent, 'is_dark_mode', False))
        
        ThemeHelper.apply_popup_theme(msg, is_dark)
        
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon_type)
        msg.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)
        msg.exec()

    @staticmethod
    def info(parent, message, title="Bilgi"):
        CustomDialogs.show_message(parent, title, message, QMessageBox.Icon.Information)

    @staticmethod
    def warning(parent, message, title="Uyarı"):
        CustomDialogs.show_message(parent, title, message, QMessageBox.Icon.Warning)

    @staticmethod
    def error(parent, message, title="Hata"):
        CustomDialogs.show_message(parent, title, message, QMessageBox.Icon.Critical)

    @staticmethod
    def question(parent, message, title="Onay"):
        msg = QMessageBox(parent)
        
        is_dark = False
        if parent:
            is_dark = getattr(parent, 'is_dark', getattr(parent, 'is_dark_mode', False))
            
        ThemeHelper.apply_popup_theme(msg, is_dark)
        
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Question)
        btn_evet = msg.addButton("Evet", QMessageBox.ButtonRole.YesRole)
        btn_hayir = msg.addButton("Hayır", QMessageBox.ButtonRole.NoRole)
        msg.exec()
        return msg.clickedButton() == btn_evet
