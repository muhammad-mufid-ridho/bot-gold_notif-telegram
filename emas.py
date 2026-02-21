import os
import requests

# Ambil data dari Environment Variables (GitHub Secrets)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOLD_API_KEY = os.getenv("GOLD_API_KEY")

def get_gold_data():
    # Menggunakan XAU/USD karena jauh lebih stabil di GoldAPI
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Cek jika ada error dari API
        if 'price' not in data:
            print("Gagal ambil data! Pesan API:", data)
            return None
        
        # 1. Ambil harga gram 24K dalam USD dari data dashboard
        harga_usd_per_gram = data.get('price_gram_24k', 0)
        
        # 2. Konversi ke Rupiah (Asumsi Kurs 1 USD = Rp 15.700)
        # Kamu bisa sesuaikan angka ini jika ingin lebih akurat
        kurs_idr = 15700
        harga_sekarang = int(harga_usd_per_gram * kurs_idr)
        
        # 3. Hitung harga kemarin (prev_close_price dalam Ounce ke Gram)
        harga_kemarin_usd = data.get('prev_close_price', 0) / 31.1035
        harga_kemarin = int(harga_kemarin_usd * kurs_idr)
        
        # 4. Harga Buyback (asumsi selisih 8% untuk pasar Indonesia)
        harga_buyback = int(harga_sekarang * 0.92)
        
        return {
            "sekarang": harga_sekarang,
            "kemarin": harga_kemarin,
            "buyback": harga_buyback,
            "persen_perubahan": data.get('chp', 0)
        }
    except Exception as e:
        print(f"Terjadi kesalahan koneksi: {e}")
        return None

def kirim_pesan():
    d = get_gold_data()
    if not d or d['sekarang'] == 0:
        print("❌ Gagal mendapatkan data emas.")
        return

    persen = d['persen_perubahan']
    
    # Logika Notifikasi: 5% jual, lainnya tunggu
    if persen >= 5:
        status = f"Naik tajam {persen}% 🚀 (Waktunya Jual!)"
    elif persen <= -5:
        status = f"Turun drastis {abs(persen)}% 📉 (Waktunya Beli!)"
    else:
        status = f"{'Naik' if persen > 0 else 'Turun'} {abs(persen)}% (Tunggu sampai 5% baru jual)"

    # Logika Selisih Buyback
    selisih_bb = d['sekarang'] - d['buyback']

    pesan = (
        f"💰 *UPDATE HARGA EMAS HARI INI*\n\n"
        f"💵 Harga: *Rp {d['sekarang']:,}/gram*\n"
        f"📈 Perubahan: {status}\n"
        f"🏦 Est. Buyback: Rp {d['buyback']:,}\n"
        f"⚖️ Selisih: Rp {selisih_bb:,}\n\n"
        f"📅 _Data dikonversi dari USD ke IDR_"
    )

    url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": pesan, 
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url_tele, data=payload)
        if res.status_code == 200:
            print("✅ Berhasil! Cek Telegram kamu.")
        else:
            print(f"❌ Gagal kirim Telegram: {res.text}")
    except Exception as e:
        print(f"❌ Error kirim Telegram: {e}")

if __name__ == "__main__":
    kirim_pesan()