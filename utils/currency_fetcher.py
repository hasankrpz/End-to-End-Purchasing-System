import urllib.request
import json
import ssl

class CurrencyFetcher:
    @staticmethod
    def get_rates(base="TRY"):
        rates = {'TRY': 1.0}
        
        try:
            # Sertifika doğrulamasını yok sayan SSL bağlamı oluştur (bazı kurumsal/exe ortamları için düzeltme)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            try:
                # Frankfurter API (Ücretsiz, anahtar gerekmez)
                # USD ve EUR'yu ayrı ayrı veya birlikte çekiyoruz
                # Strateji: USD->TRY ve EUR->TRY kurlarını çek
                url_usd = "https://api.frankfurter.app/latest?from=USD&to=TRY"
                with urllib.request.urlopen(url_usd, context=ctx, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    if 'rates' in data and 'TRY' in data['rates']:
                        rates['USD'] = float(data['rates']['TRY'])
            except Exception as e:
                print(f"USD çekilemedi: {e}")

            try:
                url_eur = "https://api.frankfurter.app/latest?from=EUR&to=TRY"
                with urllib.request.urlopen(url_eur, context=ctx, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    if 'rates' in data and 'TRY' in data['rates']:
                        rates['EUR'] = float(data['rates']['TRY'])
            except Exception as e:
                print(f"EUR çekilemedi: {e}")
                
            return rates

        except Exception as e:
            print(f"Döviz çekme kritik hatası: {e}")
            return rates # En azından TRY: 1.0 döndür
