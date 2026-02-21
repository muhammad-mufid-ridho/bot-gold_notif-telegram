import os
import requests

# Ambil data dari Environment Variables (Keamanan)
TOKEN = os.getenv("8458022961:AAE5wudtPWa-FiUBTaDqWUjvXogik5QZOfY")
CHAT_ID = os.getenv("1519188290")
GOLD_API_KEY = os.getenv("goldapi-1ne5dsmlvzlkzs-io")

def get_gold_data():
    url = "https://www.goldapi.io/api/XAU/IDR" # XAU = Emas, IDR = Rupiah
    headers = {"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # GoldAPI memberikan harga per Troy Ounce. Kita konversi ke Gram (1 Oz = 31.1g)
    harga_per_gram = int(data['price'] / 31.1)
    harga_kemarin = int(data['prev_close_price'] / 31.1)
    
    # Asumsi buyback rata-rata di Indonesia (selisih ~8% dari harga pasar)
    # Kamu bisa menyesuaikan rumus ini jika punya sumber API buyback spesifik
    harga_buyback = int(harga_per_gram * 0.92) 
    
    return harga_per_gram, harga_kemarin, harga_buyback

def kirim_pesan():
    sekarang, kemarin, buyback = get_gold_data()
    
    # 1. Hitung Persentase
    selisih_persen = ((sekarang - kemarin) / kemarin) * 100
    
    # Logika 5%
    if selisih_persen >= 5:
        status_tren = f"Naik {selisih_persen:.2f}% 🔥 (Jual Sekarang)"
    elif selisih_persen <= -5:
        status_tren = f"Turun {abs(selisih_persen):.2f}% ❄️ (Beli Lagi!)"
    else:
        status_tren = f"{'Naik' if selisih_persen > 0 else 'Turun'} {abs(selisih_persen):.2f}% (Tunggu/Jangan Jual)"

    # 2. Selisih Buyback (Spread)
    spread = sekarang - buyback
    rekomendasi_bb = "Jual Sekarang (Spread Tipis)" if spread < 50000 else "Jangan Jual (Spread Lebar)"

    teks = (
        f"💰 *UPDATE HARGA EMAS HARI INI*\n\n"
        f"💵 Harga: *Rp {sekarang:,}/gram*\n"
        f"📈 Tren: {status_tren}\n"
        f"🔄 Buyback: Rp {buyback:,}\n"
        f"⚖️ Selisih BB: Rp {spread:,} => *{rekomendasi_bb}*"
    )

    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={"chat_id": CHAT_ID, "text": teks, "parse_mode": "Markdown"})

if __name__ == "__main__":
    kirim_pesan()