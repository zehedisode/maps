import pandas as pd

def create_dataframe(places_data):
    """
    Scraper'dan gelen listeyi Pandas DataFrame'e çevirir.
    """
    if isinstance(places_data, dict) and "error" in places_data:
        return pd.DataFrame() # Hata varsa boş dön
        
    df = pd.DataFrame(places_data)
    return df

def filter_leads(df):
    """
    DataFrame içinden sadece web sitesi OLMAYANLARI filtreler.
    """
    if df.empty:
        return df
    
    # Website sütunu boş olanlar (None veya NaN) veya boş string olanlar
    # Not: Google API 'website' yoksa key olarak dönmeyebilir veya None döner.
    
    # 'website' sütunu yoksa hepsi potansiyel müşteridir (hiçbirinin sitesi yok demektir)
    if 'website' not in df.columns:
        return df
        
    # Website sütunu NaN olanları al
    no_website_df = df[df['website'].isna() | (df['website'] == '')]
    
    return no_website_df

def clean_phone_number(phone):
    """
    Telefon numarasını WhatsApp linki için temizler.
    Örn: +90 (555) 123 45 67 -> 905551234567
    """
    if not phone:
        return None
    
    # Sadece rakamları tut
    clean_num = ''.join(filter(str.isdigit, str(phone)))
    
    # Türkiye için numara formatlama (Varsayılan)
    # Eğer 0 ile başlıyorsa (Örn: 0555...) -> 90555...
    if clean_num.startswith("0"):
        clean_num = "90" + clean_num[1:]
    # Eğer 90 ile başlamıyorsa ve 10 haneli ise (Örn: 555...) -> 90555...
    elif len(clean_num) == 10:
        clean_num = "90" + clean_num
        
    return clean_num
