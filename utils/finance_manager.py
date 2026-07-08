from database.db_manager import DatabaseManager
from datetime import datetime

class FinanceManager:
    def __init__(self):
        self.db = DatabaseManager()

    def get_department_budget_status(self, department_id, year=None):
        """
        Bölümün bütçe durumunu (Toplam, Harcanan, Kalan) hesaplar.
        Harcanan = Faturalanmış Tutarlar + Açık Siparişler + Bekleyen Talepler
        (Basitlik için tümünü 'Harcanan' sayıyoruz veya kümülatif bakıyoruz)
        """
        if year is None:
            year = datetime.now().year

        self.db.connect()
        try:
            # 1. Toplam Bütçe (Yıllık + Aylıklar Toplamı)
            cursor = self.db.cursor
            cursor.execute("SELECT SUM(amount) FROM budgets WHERE department_id=? AND year=?", (department_id, year))
            total_budget = cursor.fetchone()[0] or 0.0

            # 2. Harcamalar (Faturalar - Henüz siparişle ilişki tam değilse manuel bakacağız)
            # Mevcut yapıda purchase_orders veya purchase_requests üzerinden gitmek daha sağlıklı.
            # Henüz 'purchase_orders'a 'price' kolonu eklemedik (offers tablosundan geliyor).
            # Bu sorgu biraz karmaşık olacak.

            # A. Bekleyen Talepler (Henüz siparişe dönüşmemiş)
            # talep -> ürün (ama fiyat yok! Tahmini veya Teklif yoksa 0?)
            # Fiyat bilgisi offers tablosunda kesinleşiyor. 
            # Basit olması için: Sadece "Siparişleşmiş" veya "Teklifi Seçilmiş" olanları düşelim.
            
            # B. Onaylanmış / Açık Siparişler (Faturası Henüz Girilmemiş)
            # sipariş -> teklif -> fiyat * talep.miktar
            # (Basitlik için döviz çevrimi yapmadan TL varsayıyoruz veya 'TRY' filtreliyoruz)
            
            spent_query = """
                SELECT SUM(o.price * pr.quantity)
                FROM purchase_orders po
                JOIN offers o ON po.offer_id = o.offer_id
                JOIN purchase_requests pr ON o.request_id = pr.request_id
                JOIN users u ON pr.requester_user_id = u.user_id
                WHERE u.department_id = ? 
                  AND strftime('%Y', po.created_at) = ?
                  -- AND po.status_id NOT IN (İptal Statüleri) -- Eklenebilir
            """
            cursor.execute(spent_query, (department_id, str(year)))
            spent_amount = cursor.fetchone()[0] or 0.0

            remaining = total_budget - spent_amount
            
            return {
                "total": total_budget,
                "spent": spent_amount,
                "remaining": remaining,
                "year": year
            }

        except Exception as e:
            print(f"Bütçe Hesaplama Hatası: {e}")
            return {"total": 0, "spent": 0, "remaining": 0}
        finally:
            self.db.disconnect()

    def check_budget_availability(self, department_id, amount_needed):
        """
        Bütçe kontrolü yapar.
        Return: (is_available: bool, message: str, logic_type: str)
        """
        status = self.get_department_budget_status(department_id)
        
        if status["total"] == 0:
            return False, "Bu departman için tanımlanmış bütçe bulunamadı.", "NO_BUDGET"

        if status["remaining"] < amount_needed:
            msg = (f"Bütçe Yetersiz!\n"
                   f"Kalan: {status['remaining']:,.2f} ₺\n"
                   f"İstenen: {amount_needed:,.2f} ₺\n"
                   f"Fark: {amount_needed - status['remaining']:,.2f} ₺")
            return False, msg, "INSUFFICIENT"
        
        return True, "Bütçe müsait.", "OK"
