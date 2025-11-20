import streamlit as st
import pandas as pd
import time
import random
from scraper import GoogleMapsScraper
from utils import create_dataframe, filter_leads
from messaging import WhatsAppBot, send_email

# Sayfa Ayarları
st.set_page_config(page_title="Google Maps Lead Generator", page_icon="📍", layout="wide")

# WhatsApp Botunu Cache'le (Sürekli yeniden başlamasın)
@st.cache_resource
def get_whatsapp_bot():
    return WhatsAppBot()

wa_bot = get_whatsapp_bot()

# Başlık ve Açıklama
st.title("📍 Google Maps Lead Generator")
st.markdown("""
Bu araç, Google Maps üzerinden belirli bir bölge ve sektördeki işletmeleri tarar, 
**web sitesi olmayanları** tespit eder ve onlara ulaşmanızı sağlar.
""")

# Sidebar - Ayarlar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    st.info("Bu sürüm Selenium kullanır. Google Chrome tarayıcısının yüklü olması gerekir.")
    
    st.divider()
    
    st.subheader("📧 E-posta Ayarları (Opsiyonel)")
    smtp_email = st.text_input("Gmail Adresi")
    smtp_password = st.text_input("Uygulama Şifresi", type="password", help="Gmail > Güvenlik > Uygulama Şifreleri kısmından alın.")
    
    st.divider()
    
    st.info("Geliştirici: Antigravity")

# Ana Ekran - Arama
col1, col2 = st.columns(2)

with col1:
    location = st.text_input("Konum (Şehir/İlçe)", placeholder="Örn: Kadıköy, İstanbul")
with col2:
    keyword = st.text_input("Anahtar Kelime (Sektör)", placeholder="Örn: Kuaförler, Diş Hekimleri")

search_btn = st.button("🔍 Müşteri Ara (Selenium)", type="primary")

# Session State Başlatma (Verileri tutmak için)
if 'results_df' not in st.session_state:
    st.session_state.results_df = None

if search_btn:
    if not location or not keyword:
        st.warning("Lütfen konum ve anahtar kelime girin.")
    else:
        with st.spinner(f"'{location}' bölgesindeki '{keyword}' aranıyor... Tarayıcı açılacak, lütfen bekleyin."):
            scraper = GoogleMapsScraper()
            # API Key gerekmez
            results = scraper.search_places(location, keyword)
            
            if isinstance(results, dict) and "error" in results:
                st.error(results["error"])
            else:
                df = create_dataframe(results)
                st.session_state.results_df = df
                st.success(f"Toplam {len(df)} işletme bulundu.")

# Sonuçları Gösterme
if st.session_state.results_df is not None and not st.session_state.results_df.empty:
    
    # Filtreleme Seçeneği
    show_only_leads = st.checkbox("Sadece Web Sitesi Olmayanları Göster (Potansiyel Müşteriler)", value=True)
    
    if show_only_leads:
        display_df = filter_leads(st.session_state.results_df)
        st.info(f"Web sitesi olmayan {len(display_df)} potansiyel müşteri listeleniyor.")
    else:
        display_df = st.session_state.results_df
    
    # Tablo Gösterimi
    st.dataframe(display_df, use_container_width=True)
    
    # Aksiyon Bölümü
    st.divider()
    st.subheader("💬 İletişime Geç")
    
    if not display_df.empty:
        selected_business = st.selectbox("İşlem yapılacak işletmeyi seçin:", display_df['name'].tolist())
        
        # Seçilen işletmenin verilerini al
        business_data = display_df[display_df['name'] == selected_business].iloc[0]
        
        col_wa, col_mail = st.columns(2)
        
        with col_wa:
            st.markdown("### 📱 WhatsApp Otomasyonu")
            default_msg = f"Merhaba {business_data['name']}, Google Maps üzerinde işletmenizi gördüm ve web siteniz olmadığını fark ettim. Size özel bir web sitesi teklifimiz var."
            message_text = st.text_area("Mesaj Taslağı", value=default_msg, height=100)
            
        # Tekli Gönderim
        if st.button("WhatsApp'tan Otomatik Gönder (Tekli)"):
            if business_data.get('phone'):
                with st.spinner("WhatsApp Web açılıyor... Lütfen QR kod gerekirse okutun."):
                    success, msg = wa_bot.send_message(business_data['phone'], message_text)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            else:
                st.warning("Bu işletmenin telefon numarası yok.")

        st.divider()
        
        # Toplu Gönderim Bölümü
        st.markdown("### 🚀 Toplu Gönderim")
        st.warning("DİKKAT: Çok hızlı mesaj göndermek WhatsApp tarafından spam olarak algılanabilir. Bu mod, her mesaj arasında rastgele 10-20 saniye bekler.")
        
        if st.button("Listelenen HERKESE Gönder (Toplu)", type="primary"):
            # İlerleme çubuğu
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_leads = len(display_df)
            success_count = 0
            fail_count = 0
            
            # Durdurma butonu için placeholder (Streamlit'te tam durdurma zordur ama flag kullanabiliriz)
            stop_button = st.empty()
            # stop = stop_button.button("Durdur") # Döngü içinde kontrol edilemez, basit tutalım
            
            for i, (index, row) in enumerate(display_df.iterrows()):
                name = row['name']
                phone = row.get('phone')
                
                status_text.text(f"İşleniyor ({i+1}/{total_leads}): {name}")
                
                if not phone:
                    status_text.text(f"Atlandı ({name}): Telefon yok.")
                    fail_count += 1
                    continue
                
                # Mesajı kişiselleştir
                # Kullanıcı {name} placeholder'ı kullandıysa değiştir, yoksa direkt metni al
                # Basitlik için: Kullanıcının girdiği metni kullanıyoruz. 
                # Eğer metin içinde "{name}" varsa replace edebiliriz ama şimdilik basit tutalım.
                # Ancak kullanıcı tekli gönderimde ismi otomatik alıyordu, burada da almalı.
                # Tekli gönderimdeki default_msg mantığını buraya uyarlayalım.
                
                # Not: Kullanıcı text_area'da metni değiştirdiyse o metni kullanırız.
                # Ancak "Merhaba {business_data['name']}" kısmı hardcoded idi.
                # Kullanıcı text_area'yı değiştirdiğinde oradaki isim sabit kalır.
                # Bu yüzden toplu gönderimde ismi dinamik değiştirmek için text_area'daki metni şablon olarak kullanamayız
                # eğer kullanıcı ismi elle yazdıysa.
                # Çözüm: Kullanıcıya jenerik bir mesaj yazdırmak veya "{isim}" placeholder'ı kullandırtmak.
                # Şimdilik: Kullanıcının girdiği metni olduğu gibi gönderelim, 
                # ama eğer metin içinde seçili işletmenin adı geçiyorsa onu yeni işletme adıyla değiştirmeye çalışalım (Riskli).
                # En güvenlisi: Kullanıcıya uyarı verip, metni olduğu gibi göndermek.
                
                # VEYA: Otomatik mesaj oluşturucu kullanalım:
                current_msg = f"Merhaba {name}, Google Maps üzerinde işletmenizi gördüm ve web siteniz olmadığını fark ettim. Size özel bir web sitesi teklifimiz var."
                
                try:
                    success, msg = wa_bot.send_message(phone, current_msg)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        st.toast(f"Hata ({name}): {msg}")
                except Exception as e:
                    fail_count += 1
                    st.error(f"Kritik Hata: {e}")
                
                # İlerleme güncelle
                progress_bar.progress((i + 1) / total_leads)
                
                # Bekleme (Son eleman değilse)
                if i < total_leads - 1:
                    wait_time = random.uniform(10, 20)
                    status_text.text(f"{name} tamamlandı. {int(wait_time)} saniye bekleniyor...")
                    time.sleep(wait_time)
            
            status_text.text("İşlem Tamamlandı!")
            st.success(f"Toplu Gönderim Bitti! Başarılı: {success_count}, Başarısız: {fail_count}")
            st.balloons()
                
        with col_mail:
            st.markdown("### 📧 E-posta Otomasyonu")
            email_subject = st.text_input("Konu", value="Web Sitesi Teklifi")
            email_body = st.text_area("E-posta İçeriği", value=default_msg, height=100, key="email_body")
            target_email = st.text_input("Alıcı E-posta", placeholder="isletme@mail.com (Manuel Girin)") 
            
            if st.button("E-posta Gönder"):
                if not smtp_email or not smtp_password:
                    st.error("Lütfen sol menüden E-posta ayarlarını yapın.")
                elif not target_email:
                    st.error("Lütfen alıcı e-posta adresi girin.")
                else:
                    smtp_config = {
                        'server': 'smtp.gmail.com',
                        'port': 587,
                        'email': smtp_email,
                        'password': smtp_password
                    }
                    success, msg = send_email(target_email, email_subject, email_body, smtp_config)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

else:
    if st.session_state.results_df is not None:
        st.warning("Sonuç bulunamadı veya filtrelendi.")
