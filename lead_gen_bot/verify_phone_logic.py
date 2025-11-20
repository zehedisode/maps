from utils import clean_phone_number

def test_phone_logic():
    test_cases = [
        "+90 555 123 45 67",  # Standard international
        "0555 123 45 67",     # Local with 0
        "555 123 45 67",      # Local without 0
        "+90 (212) 123 4567", # Landline international
        "0212 123 45 67",     # Landline local
    ]

    print("--- Telefon Numarası Mantık Testi ---")
    for phone in test_cases:
        cleaned = clean_phone_number(phone)
        print(f"Girdi: '{phone}' -> Çıktı: '{cleaned}'")
        
        # WhatsApp URL kontrolü
        # WhatsApp genelde ülke kodu ister (90...)
        # Eğer 0 ile başlıyorsa ve ülke kodu yoksa sorun olabilir.
        if cleaned.startswith("0"):
            print(f"  UYARI: Numara '0' ile başlıyor. WhatsApp Web ülke kodu bekleyebilir.")
        elif len(cleaned) == 10:
             print(f"  UYARI: Numara 10 haneli (ülke kodu yok). WhatsApp Web hata verebilir.")
        else:
            print(f"  Durum: Görünüşe göre geçerli format (veya ülke kodlu).")

if __name__ == "__main__":
    test_phone_logic()
