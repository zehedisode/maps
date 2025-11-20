import time
from messaging import WhatsAppBot

def test_whatsapp():
    print("--- WhatsApp Test Başlatılıyor ---")
    print("Tarayıcı açılacak. Lütfen QR kodunu okutun.")
    
    bot = WhatsAppBot()
    
    # Rastgele bir numara ile test et (Mesaj gönderilmeyecek, sadece kutu aranacak)
    # Kendi numaranızı veya test numaranızı buraya yazabilirsiniz, ama kutuyu bulmak için numara şart.
    # 905555555555 gibi geçersiz bir numara olsa bile WhatsApp Web sohbet ekranını açar (numara kayıtlı değil derse bile).
    # Ancak en iyisi geçerli bir format.
    test_phone = "905320000000" 
    test_message = "Bu bir test mesajıdır."
    
    try:
        print("Bot başlatılıyor...")
        bot.setup_driver()
        
        print(f"Test numarasına gidiliyor: {test_phone}")
        url = f"https://web.whatsapp.com/send?phone={test_phone}"
        bot.driver.get(url)
        
        print("Lütfen QR kodunu okutun! (60 saniye beklenecek)")
        
        # send_message fonksiyonunu simüle et, ama sadece kutuyu bulma kısmını
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(bot.driver, 60)
        
        # Login kontrolü
        try:
            print("Giriş yapılması bekleniyor...")
            wait.until(EC.presence_of_element_located((By.ID, "side")))
            print("Giriş başarılı!")
        except:
            print("Giriş zaman aşımına uğradı veya yapılamadı.")
            bot.close()
            return

        print("Mesaj kutusu aranıyor...")
        
        # messaging.py'deki GÜNCEL mantığı kopyalıyorum test için
        input_box = None
        # Önce main pane'i bekle
        try:
            wait.until(EC.presence_of_element_located((By.ID, "main")))
            print("Sohbet penceresi (main) yüklendi.")
        except:
            print("Sohbet penceresi yüklenemedi (Numara geçersiz olabilir).")

        potential_xpaths = [
            '//footer//div[@contenteditable="true"][@role="textbox"]', 
            '//footer//div[@role="textbox"]', 
            '//div[@id="main"]//footer//div[@contenteditable="true"]', 
        ]

        found_xpath = None
        for xpath in potential_xpaths:
            try:
                print(f"Deneniyor: {xpath}")
                input_box = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                if input_box:
                    found_xpath = xpath
                    break
            except:
                continue
        
        if input_box:
            print(f"BAŞARILI! Mesaj kutusu bulundu. Çalışan seçici: {found_xpath}")
            print("Test tamamlandı.")
        else:
            print("BAŞARISIZ! Mesaj kutusu bulunamadı.")
            
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        print("Tarayıcı kapatılıyor...")
        time.sleep(5) # Kullanıcının sonucu görmesi için bekle
        bot.close()

if __name__ == "__main__":
    test_whatsapp()
