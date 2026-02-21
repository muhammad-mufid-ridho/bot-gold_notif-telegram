import os
import requests

# Ambil data dari Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOLD_API_KEY = os.getenv("GOLD_API_KEY")

def get_gold_data():
    url = "https://www.goldapi.io/api/XAU/IDR"
    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if 'price' not in data:
            print("Gagal ambil data! Respon API:", data)
            return None
        
        # Kalkulasi Harga
        # 1 Troy Ounce = 31.1035 gram
        harga_per_gram = int(data['price'] / 31.1035)
        harga_kemarin = int(data['prev_close_price'] / 31.1035)
        
        # Estimasi harga buyback (umumnya selisih 8-10% di Indonesia)
        harga_buyback = int(harga_per_gram * 0.92) 
        
        return {
            "sekarang": harga_per_gram,
            "kemarin": harga_kemarin,
            "buyback": harga_buyback,
            "persen_perubahan": data.get('chp', 0) # Persentase dari API
        }
    except Exception as e:
        print(f"Error Koneksi: {e}")
        return None

def kirim_pesan():
    d = get_gold_data()
    
    if not d:
        return

    # 1. Logika Persentase (Kriteria 5%)
    # Kita gunakan data perubahan harian dari API
    persen = d['persen_perubahan']
    
    if persen >= 5:
        status_harga = f"Naik drastis {persen:.2f}% 🚀 (Jual Sekarang!)"
    elif persen > 0:
        status_harga = f"Naik {persen:.2f}% (Jangan Jual, Tunggu 5%)"
    elif persen <= -5:
        status_harga = f"Turun drastis {abs(persen):.2f}% 📉 (Waktunya Serok/Beli!)"
    else:
        status_harga = f"Turun {abs(persen):.2f}% (Jangan Jual)"

    # 2. Logika Selisih Buyback
    selisih_bb = d['sekarang'] - d['buyback']
    # Jika selisih tipis (misal < 50rb), biasanya momen bagus untuk jual
    rekomendasi_bb = "Jual sekarang" if selisih_bb < 70000 else "Jangan jual"

    pesan = (
        f"🔔 *NOTIFIKASI HARGA EMAS*\n\n"
        f"💰 Harga Sekarang: *Rp {d['sekarang']:,}/gram*\n"
        f"📊 Tren: {status_harga}\n"
        f"🔄 Harga Buyback: Rp {d['buyback']:,}\n"
        f"⚖️ Selisih Buyback: Rp {selisih_bb:,} => *{rekomendasi_bb}*"
    )

    url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    
    res = requests.post(url_tele, data=payload)
    if res.status_code == 200:
        print("✅ Notifikasi berhasil dikirim!")
    else:
        print(f"❌ Gagal kirim Telegram: {res.text}")

if __name__ == "__main__":
    kirim_pesan()