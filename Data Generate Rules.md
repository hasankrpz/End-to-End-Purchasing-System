# DATA GENERATION RULES

Bu dosya, sisteme sahte/test verisi basarken (seeding) veya manuel veri girerken uyulması gereken **iş mantığı ve tutarlılık kurallarını** içerir. Amaç, raporların ve dashboard'un anlamlı görünmesini sağlamaktır.

## 1. TEMEL ENTITY İLİŞKİLERİ (Zincir Kuralı)
Veri oluştururken aşağıdaki yaşam döngüsü takip edilmelidir:
`Talep (Request)` -> `Teklif (Offer)` -> `Sipariş (Order)` -> `Fatura (Invoice)` -> `Ödeme (Payment)`

### Detaylı Akış:
1.  **Satın Alma Talebi (Request):** Kullanıcı bir ürün için miktar belirtir.
2.  **Teklifler (Offers):** Her talep için **1 ile 4 arasında** tedarikçi teklifi oluşturulur.
3.  **Sipariş (Order):** 
    *   Siparişe dönen talep için tekliflerden **SADECE BİRİ** 'Seçildi' (ID: ? - genelde 3) durumuna geçer.
    *   Diğer teklifler 'Reddedildi' (ID: ? - genelde 2) olur.
    *   Sipariş tablosunda `exchange_rate` (Sipariş Anındaki Kur)  kaydedilir.
4.  **Fatura (Invoice):**
    *   "Teslim Alındı" durumundaki siparişler için fatura kesilir.
    *   `invoice_no` formatı: `INV-{YIL}-{RastgeleSayi}` (Örn: INV-2025-10293).
    *   `exchange_rate` (Fatura Anındaki Kur) kaydedilir. **Kur Farkı Raporu için sipariş kuru ile farklı olabilir.**
    *   `status_id` alanı **Integer** olarak tutulur (Tablo şemasında TEXT görünse bile uygulama ID kullanır).
5.  **Ödeme (Payment):**
    *   Faturaya bağlı ödemeler yapılır.
    *   Parçalı ödeme veya tam ödeme olabilir.

---

## 2. DURUM (STATUS) ID TANIMLARI
Uygulama kodunda kullanılan standart ID'ler (Değişirse burayı güncelle):

**Talep Durumları (`request_statuses`):**
*   `Bekliyor`: Henüz teklif toplanıyor.
*   `Onaylandı`: Yönetici onayladı, teklif seçimi bekleniyor.
*   `Tamamlandı`: Siparişe dönüştü.
*   `İptal Edildi`: İptal.

**Sipariş Durumları (`order_statuses`):**
*   `Bekliyor`: Tedarikçiye iletildi.
*   `Teslim Alındı`: Ürünler geldi (Fatura kesilebilir).
*   `İptal`: İptal.

**Fatura Durumları (`invoice_statuses`):**
*   `1` -> **Ödendi** (Paid) - Bakiyesi 0.
*   `2` -> **Bekliyor** (Pending) - Hiç ödeme yok.
*   `3` -> **Kısmi** (Partial) - Bir miktar ödenmiş.
*   `4` -> **İptal** (Varsa).

---

## 3. TARİH VE ZAMANLAMA MANTIĞI
Tarihler mantıksal sıraya uymalıdır:

*   **Talep Tarihi (`T0`):** Referans başlangıç.
*   **Teklif Tarihi:** `T0` + (1-3 Gün).
*   **Sipariş Tarihi:** En son teklif tarihinden + (1-5 Gün) sonra.
*   **Teslim Tarihi:** Sipariş tarihinden + (3-15 Gün) sonra.
*   **Fatura Tarihi:** Genellikle teslim tarihi ile aynı veya + (0-7 Gün) sonra.
*   **Vade Tarihi (Due Date):** Fatura tarihinden + (15, 30, 45, 60 Gün) sonra.
*   **Ödeme Tarihi:** Fatura tarihi ile Vade tarihi arasında bir gün.

---

## 4. PARA BİRİMİ VE KUR SİMÜLASYONU
Raporların dolu görünmesi için:

*   **Dağılım:** İşlemlerin %40'ı **TRY**, %30'u **USD**, %30'u **EUR** olmalı.
*   **Kur Değerleri:**
    *   Geçmişe dönük veri üretirken kurun zamanla arttığı bir simülasyon kullan (Örn: Yılbaşında 30, Yıl sonunda 45).
    *   **Kur Riski:** Sipariş (`purchase_orders.exchange_rate`) ile Fatura (`invoices.exchange_rate`) arasında rastgele küçük farklar (+/- %5) oluştur. Bu, "Kur Farkı / Risk Analizi" raporunu anlamlı kılar.

---

## 5. ÖDEME YÖNTEMLERİ
Mevcut 4 ödeme yöntemi vardır ve eşit dağıtılmalıdır:
1.  **Banka Havalesi**
2.  **Kredi Kartı**
3.  **Çek**
4.  **Nakit**

---

## 6. BÜTÇE VE DEPARTMANLAR
*   **Departmanlar:** IT, İK, Üretim, Pazarlama, Satınalma vb.
*   **Bütçe:** Her departman için yıllık bütçe tanımlanmalı.
*   **Kural:** Departman bütçeleri, o departmanın toplam harcamasından bir miktar fazla olmalı (Örn: Harcama * 1.25) ki bütçe aşımı hemen görünmesin ama doluluk oranları (%80-90) gerçekçi dursun.

---

## 7. VERİ BÜYÜKLÜĞÜ (HEDEFLER)
*   **Toplam Fatura:** ~500+ adet.
*   **Açık Fatura (Bekliyor):** Az sayıda (Örn: 9-10 adet). Kullanıcı "İşler kontrol altında" hissetmeli.
*   **Aktif Tedarikçi:** 20-50 arası.
*   **Tedarikçi Bakiyesi:** Birkaç tedarikçide yüksek borç bakiyesi bırakarak "Tedarikçi Ekstresi" raporunda veri oluşmasını sağla.

---

## 8. TEKNİK DETAYLAR
*   **Floating Point:** Tüm parasal değerler (Tutar, Vergi, Ödeme) veritabanına kaydedilmeden önce **2 ondalık basamağa yuvarlanmalı** (`round(x, 2)`). Aksi takdirde `-0.00000002` gibi bakiye hataları oluşur.
*   **Türkçe Karakter:** İsimlerde ve açıklamalarda Türkçe karakter (ç, ğ, ı, ö, ş, ü) kullanılabilir ve teşvik edilir.