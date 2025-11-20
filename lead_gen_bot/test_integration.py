from messaging import WhatsAppBot
from utils import clean_phone_number
import time

def test_integration_flow():
    print("--- ENTEGRASYON TESTİ BAŞLIYOR ---")
    print("Senaryo: Google Maps'ten '0212 123 45 67' numaralı bir işletme çekildi.")
    
    # 1. Mock Data (Google Maps'ten gelmiş gibi)
    mock_maps_data = {
        "name": "Örnek İşletme",
        "phone": "0 (212) 123 45 67", # Zorlu format
        "website": None
    }
    print(f"1. Ham Veri: {mock_maps_data}")
    
    # 2. Data Cleaning (Utils)
    raw_phone = mock_maps_data['phone']
    clean_phone = clean_phone_number(raw_phone)
    print(f"2. Temizlenmiş Numara: {clean_phone}")
    
    if not clean_phone.startswith("90"):
        print("HATA: Numara uluslararası formata çevrilemedi!")
        return

    # 3. WhatsApp Bot Simulation
    print("3. WhatsApp Bot Başlatılıyor...")
    bot = WhatsAppBot()
    
    try:
        bot.setup_driver()
        
        # 4. Navigation
        target_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
        print(f"4. Hedef URL: {target_url}")
        print("   (Tarayıcı bu adrese gidiyor...)")
        bot.driver.get(target_url)
        
        # 5. Selector Verification
        print("5. Mesaj Kutusu Kontrolü (QR Kod okutulmuş olmalı)...")
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(bot.driver, 60)
        
        # Main pane bekle
        try:
            wait.until(EC.presence_of_element_located((By.ID, "main")))
            print("   ✅ Sohbet penceresi yüklendi (Numara geçerli).")
        except:
            print("   ⚠️ Sohbet penceresi gelmedi (Numara geçersiz olabilir veya giriş yapılmadı).")
            # Test için devam ediyoruz, belki footer yine de vardır (nadiren)
            
        # Footer içindeki kutuyu ara
        try:
            box = wait.until(EC.presence_of_element_located((By.XPATH, '//footer//div[@contenteditable="true"][@role="textbox"]')))
            print("   ✅ BAŞARILI: Mesaj kutusu DOĞRU SEÇİCİ ile bulundu.")
            print("   Bu, botun arama çubuğuna değil, mesaj kutusuna yazacağını kanıtlar.")
        except:
            print("   ❌ HATA: Mesaj kutusu bulunamadı.")
            
    except Exception as e:
        print(f"Test Hatası: {e}")
    finally:
        print("Test tamamlandı. Tarayıcı kapatılıyor.")
        bot.close()

if __name__ == "__main__":
    test_integration_flow()
