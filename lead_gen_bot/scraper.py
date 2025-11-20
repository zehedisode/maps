import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class GoogleMapsScraper:
    def __init__(self):
        """
        Selenium tabanlı Google Maps Scraper başlatıcı.
        """
        self.driver = None

    def setup_driver(self):
        """
        Chrome Driver'ı başlatır ve ayarlar.
        """
        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Hata ayıklama için başsız modu kapalı tutuyoruz
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def search_places(self, location, keyword, max_results=10):
        """
        Belirli bir konum ve anahtar kelimeye göre işletmeleri arar.
        """
        if not self.driver:
            self.setup_driver()

        results = []
        try:
            # 1. Google Maps'e git
            self.driver.get("https://www.google.com/maps")
            
            # 2. Arama yap
            wait = WebDriverWait(self.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            search_box.clear()
            search_box.send_keys(f"{keyword} in {location}")
            search_box.send_keys(Keys.ENTER)
            
            # 3. Sonuçların yüklenmesini bekle
            # İlk sonucun görünmesini bekle (a.hfpxzc class'ı genelde sonuç linkidir)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.hfpxzc")))
            time.sleep(3) # Ekstra bekleme

            # 4. Scroll işlemi (Daha fazla sonuç yüklemek için)
            # Sonuçların olduğu paneli bul (role="feed")
            feed_panel = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            
            # Birkaç kez scroll yap
            for _ in range(3):
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed_panel)
                time.sleep(2)

            # 5. Sonuçları topla
            place_links = self.driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            print(f"Bulunan toplam sonuç: {len(place_links)}")
            
            # İstenen sayı kadarını işle
            for i, link in enumerate(place_links[:max_results]):
                try:
                    # Görünür olması için scroll et
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    link.click()
                    time.sleep(2) # Detayların yüklenmesi için bekle
                    
                    place_details = self.extract_details()
                    if place_details:
                        results.append(place_details)
                        
                except Exception as e:
                    print(f"Sonuç işleme hatası ({i}): {e}")
                    continue

        except Exception as e:
            print(f"Genel Hata: {e}")
            return {"error": str(e)}
        finally:
            # Tarayıcıyı kapatma (Streamlit tekrar çalıştırınca sorun olmaması için kapatıyoruz, 
            # ama kullanıcı görmek isterse açık bırakılabilir. Şimdilik kapatalım.)
            if self.driver:
                self.driver.quit()
                self.driver = None
                
        return results

    def extract_details(self):
        """
        Açık olan detay panelinden bilgileri çeker.
        """
        try:
            # İsim (Genelde h1 etiketi)
            try:
                name = self.driver.find_element(By.TAG_NAME, "h1").text
            except:
                name = "İsimsiz"

            # Telefon
            phone = None
            try:
                # Aria-label içinde "Telefon" geçen veya data-item-id="phone" olan buton
                phone_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                phone = phone_btn.get_attribute("aria-label").replace("Telefon: ", "").strip()
            except:
                pass

            # Web Sitesi
            website = None
            try:
                # Aria-label içinde "Web sitesi" geçen veya data-item-id="authority" olan buton
                website_btn = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                website = website_btn.get_attribute("href")
            except:
                pass
            
            # Adres
            address = None
            try:
                 address_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
                 address = address_btn.get_attribute("aria-label").replace("Adres: ", "").strip()
            except:
                pass

            # Maps Linki
            maps_url = self.driver.current_url

            return {
                "name": name,
                "phone": phone,
                "address": address,
                "website": website,
                "maps_url": maps_url
            }

        except Exception as e:
            print(f"Detay çekme hatası: {e}")
            return None
