import os
import time
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip
from utils import clean_phone_number

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.profile_path = os.path.join(os.getcwd(), "whatsapp_profile")
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)

    def setup_driver(self):
        if self.driver is not None:
            return

        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={self.profile_path}")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def send_message(self, phone, message):
        """
        WhatsApp Web üzerinden mesaj gönderir.
        """
        clean_num = clean_phone_number(phone)
        if not clean_num:
            return False, "Geçersiz telefon numarası."

        try:
            self.setup_driver()
            
            # Mesaj linkini oluştur (Sadece numara ile git, mesajı biz yazacağız)
            url = f"https://web.whatsapp.com/send?phone={clean_num}"
            
            self.driver.get(url)
            
            # Login kontrolü (QR kod bekleme)
            wait = WebDriverWait(self.driver, 60)
            try:
                wait.until(EC.presence_of_element_located((By.ID, "side")))
            except:
                return False, "Giriş zaman aşımına uğradı. Lütfen QR kodu daha hızlı okutun."

            # Mesaj kutusunun yüklenmesini bekle
            try:
                # Önce sohbet penceresinin (main pane) yüklendiğinden emin ol
                # Bu, arama çubuğuna yazma hatasını önlemek için kritiktir
                wait.until(EC.presence_of_element_located((By.ID, "main")))

                # Mesaj kutusu seçicileri - Sadece footer içindekilere odaklan
                input_box = None
                potential_xpaths = [
                    '//footer//div[@contenteditable="true"][@role="textbox"]', # En güvenilir
                    '//footer//div[@role="textbox"]', # Alternatif footer textbox
                    '//div[@id="main"]//footer//div[@contenteditable="true"]', # Main içindeki footer
                ]

                for xpath in potential_xpaths:
                    try:
                        input_box = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                        if input_box:
                            break
                    except:
                        continue
                
                if not input_box:
                    raise Exception("Mesaj kutusu (footer içinde) bulunamadı.")

                time.sleep(1) 
                
                # Kutuya tıkla ve odaklan
                input_box.click()
                time.sleep(0.5)
                
                # YÖNTEM DEĞİŞİKLİĞİ: Kopyala - Yapıştır (Ctrl+V)
                # Bu yöntem React tabanlı sitelerde harf harf yazmaktan daha güvenilirdir.
                pyperclip.copy(message)
                
                actions = ActionChains(self.driver)
                # Ctrl+V yap (Mac için Command+V gerekebilir ama Windows kullanıcısı olduğu için Ctrl)
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                
                time.sleep(1)
                actions.send_keys(Keys.ENTER).perform()
                
                time.sleep(2) # Gönderim için bekle
                return True, "Mesaj başarıyla gönderildi."
            except Exception as e:
                return False, f"Mesaj kutusu bulunamadı veya etkileşim hatası. Detay: {str(e)}"

        except Exception as e:
            return False, f"Otomasyon hatası: {str(e)}"

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

def send_email(to_email, subject, body, smtp_config):
    """
    SMTP kullanarak e-posta gönderir.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['email']
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['email'], smtp_config['password'])
        text = msg.as_string()
        server.sendmail(smtp_config['email'], to_email, text)
        server.quit()
        return True, "E-posta başarıyla gönderildi."
    except Exception as e:
        return False, f"E-posta gönderme hatası: {str(e)}"
