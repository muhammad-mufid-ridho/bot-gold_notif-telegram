import os
import requests

# Ambil data dari Environment Variables (GitHub Secrets)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOLD_API_KEY = os.getenv("GOLD_API_KEY")

def get_kurs_idr():
    """Mengambil kurs USD ke IDR terbaru secara gratis"""
    try:
        # Menggunakan API publik tanpa key untuk kurs
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url)
        data = response.json()
        if data.get('result') == 'success':
            return data['rates']['IDR']
        return 15700  # Angka cadangan jika API kurs gagal
    except:
        return 15700

def get_gold_data():
    kurs_idr = get_kurs_idr()
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if 'price' not in data:
            print("Gagal ambil data! Pesan API:", data)
            return None
        
        # 1. Harga emas per gram (USD) dari API
        harga_usd_per_gram = data.get('price_gram_24k', 0)
        
        # 2. Konversi ke Rupiah menggunakan kurs terbaru
        harga_sekarang = int(harga_usd_per_gram * kurs_idr)
        
        # 3. Hitung harga kemarin (prev_close)
        harga_kemarin_usd = data.get('prev_close_price', 0) / 31.1035
        harga_kemarin = int(harga_kemarin_usd * kurs_idr)
        
        # 4. Harga Buyback (asumsi selisih 8%)
        harga_buyback = int(harga_sekarang * 0.92)
        
        return {
            "sekarang": harga_sekarang,
            "kemarin": harga_kemarin,
            "buyback": harga_buyback,
            "persen_perubahan": data.get('chp', 0),
            "kurs": kurs_idr
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def kirim_pesan():
    d = get_gold_data()
    if not d or d['sekarang'] == 0:
        return

    persen = d['persen_perubahan']
    
    # Logika 5%
    if persen >= 5:
        status = f"Naik tajam {persen}% 🚀 (Jual Sekarang!)"
    elif persen <= -5:
        status = f"Turun drastis {abs(persen)}% 📉 (Serok/Beli!)"
    else:
        status = f"{'Naik' if persen > 0 else 'Turun'} {abs(persen)}% (Tunggu sampai 5%)"

    pesan = (
        f"🔔 *UPDATE HARGA EMAS REAL-TIME*\n\n"
        f"💵 Harga: *Rp {d['sekarang']:,}/gram*\n"
        f"📈 Perubahan: {status}\n"
        f"🏦 Est. Buyback: Rp {d['buyback']:,}\n"
        f"💱 Kurs USD/IDR: Rp {d['kurs']:,}\n\n"
        f"⚖️ Selisih harga jual-beli: Rp {d['sekarang'] - d['buyback']:,}"
    )

    url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    
    res = requests.post(url_tele, data=payload)
    if res.status_code == 200:
        print(f"✅ Berhasil! Kurs saat ini: Rp {d['kurs']}")
    else:
        print("❌ Gagal kirim Telegram")

if __name__ == "__main__":
    kirim_pesan()