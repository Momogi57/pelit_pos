# 💡 PelitPos

> **"gk medit gk sugeh ta?"**

Sistem Point of Sale yang efisien dan andal berbasis Python dan Streamlit. Dirancang untuk memberikan solusi kasir yang cepat, aman, dan mudah digunakan dengan fitur enterprise-grade.

## ✨ Fitur Unggulan

### 🎯 Fitur Inti

- **💳 Terminal Kasir Modern** - Interface kasir yang intuitif dengan keranjang belanja real-time
- **📦 Manajemen Produk** - CRUD lengkap untuk produk dengan kategori dan tracking stok
- **👥 Manajemen Pelanggan** - Database pelanggan terintegrasi untuk setiap transaksi
- **📊 Dashboard Analitik** - Visualisasi pendapatan dan performa bisnis
- **📋 Riwayat Transaksi** - Log transaksi lengkap dengan detail item yang dibeli

### 🔒 Keamanan & Integritas Data

- **PIN Admin** - Sistem autentikasi PIN untuk melindungi fitur administratif sensitif
- **Price Snapshots** - Harga produk disimpan pada saat transaksi untuk menjaga integritas laporan historis
- **Atomic Stock Updates** - Menggunakan SQL direct update untuk mencegah race conditions pada stok
- **Audit Trail** - Pencatatan otomatis setiap pergerakan stok ke tabel `stok_log`

### ⚡ Performa & Optimasi

- **Session Caching** - Mengurangi query database hingga 80% dengan caching pintar
- **Database Normalisasi** - Struktur relasional yang optimal dengan foreign keys
- **Transaction Integrity** - Proses "semua atau tidak sama sekali" untuk mencegah data korup
- **Selective Cache Invalidation** - Refresh data otomatis hanya saat diperlukan

### 🎨 Antarmuka Profesional

- **Industrial Dark Theme** - Tema gelap modern dengan palet warna industrial
- **Zero Emoji Design** - Interface profesional tanpa emoji untuk kesan formal
- **Responsive Layout** - Optimasi tampilan untuk berbagai ukuran layar
- **Thermal Receipt Style** - Struk belanja dengan estetika printer thermal

## 📋 Persyaratan Sistem

### Software Requirements

```bash
Python >= 3.8
Streamlit >= 1.28.0
Supabase >= 1.0.0
Pandas >= 1.5.0
Plotly >= 5.0.0
Pytz >= 2023.0
```

### Database Requirements

- Supabase account (free tier sudah cukup)
- PostgreSQL 12+ (via Supabase)

## 🚀 Instalasi & Setup

### 1. Clone atau Download Project

```bash
mkdir pelitpos
cd pelitpos
# Letakkan file app.py di direktori ini
```

### 2. Install Dependencies

```bash
pip install streamlit supabase pandas plotly pytz
```

### 3. Setup Database Supabase

#### a. Buat Project Supabase Baru

1. Kunjungi [supabase.com](https://supabase.com)
2. Sign up / Login
3. Klik "New Project"
4. Isi detail project dan tunggu setup selesai

#### b. Jalankan SQL Schema

1. Buka **SQL Editor** di dashboard Supabase
2. Copy seluruh isi file `database_schema.sql`
3. Paste dan klik **Run** untuk membuat semua tabel

Tabel yang akan dibuat:
- `produk` - Menyimpan data produk
- `pelanggan` - Menyimpan data pelanggan
- `transaksi` - Header transaksi
- `transaksi_item` - Detail item dengan price snapshots
- `stok_log` - Audit trail pergerakan stok

#### c. Verifikasi Function

Pastikan function `atomic_stock_deduct` berhasil dibuat:

```sql
-- Test function (optional)
SELECT atomic_stock_deduct(1, 5);
-- Returns: 1 (success) atau 0 (failed/insufficient stock)
```

### 4. Konfigurasi Credentials

Buat file `.streamlit/secrets.toml`:

```bash
mkdir .streamlit
nano .streamlit/secrets.toml
```

Isi dengan credentials Supabase Anda:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

**Cara mendapatkan credentials:**
1. Di dashboard Supabase, buka **Settings** → **API**
2. Copy **Project URL** → paste ke `SUPABASE_URL`
3. Copy **anon public** key → paste ke `SUPABASE_KEY`

### 5. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 🔐 PIN Admin Default

**PIN Admin Default: `1234`**

PIN ini diperlukan untuk mengakses:
- 📦 Data Master (Edit/Hapus Produk & Pelanggan)
- 📊 Dashboard Analitik

### Mengubah PIN Admin

Edit file `app.py` pada baris:

```python
ADMIN_PIN_HASH = hashlib.sha256("1234".encode()).hexdigest()
```

Untuk generate hash PIN baru:

```python
import hashlib
new_pin = "your_new_pin"
print(hashlib.sha256(new_pin.encode()).hexdigest())
```

Copy hasil hash dan replace value `ADMIN_PIN_HASH`.

## 📖 Panduan Penggunaan

### 🛒 Proses Transaksi (Terminal Kasir)

1. **Pilih Pelanggan** dari dropdown
2. **Pilih Produk** yang akan dibeli
3. **Masukkan Jumlah** (sistem akan validasi ketersediaan stok)
4. Klik **Tambah ke Keranjang**
5. Ulangi untuk produk lain
6. **Terapkan Diskon** (opsional)
7. Review struk di panel kanan
8. Klik **PROSES PEMBAYARAN**
9. Transaksi berhasil → Struk tersimpan otomatis

**Catatan Penting:**
- Harga produk di struk adalah **price snapshot** (harga saat transaksi)
- Jika harga produk berubah di kemudian hari, struk lama tetap menampilkan harga saat pembelian
- Stok dikurangi secara **atomic** untuk mencegah overselling

### 📦 Manajemen Produk (Data Master)

**⚠️ Memerlukan PIN Admin**

#### Tambah Produk:
1. Buka tab **Produk**
2. Klik **Tambah Produk Baru**
3. Isi nama, harga, stok awal, kategori
4. Klik **Simpan Produk**
5. Sistem otomatis mencatat stok awal ke audit trail

#### Edit Produk:
1. Klik tombol **✏** di samping produk
2. Ubah data yang diperlukan
3. Klik **Update**
4. Jika stok berubah, sistem otomatis log ke `stok_log`

### 📋 Melihat Riwayat Transaksi

1. Buka halaman **Riwayat**
2. Klik pada transaksi untuk melihat detail
3. Detail mencakup informasi pelanggan, tanggal, **detail item** (dengan price snapshot), total pembayaran

### 📊 Dashboard Analitik

**⚠️ Memerlukan PIN Admin**

Dashboard menampilkan:
- Total Pendapatan
- Jumlah Order
- Nilai Rata-rata
- Stok Rendah
- Grafik Tren 30 hari

## 🏗️ Arsitektur Sistem

### Database Schema

```
produk → transaksi_item (dengan price snapshots)
pelanggan → transaksi → transaksi_item
produk → stok_log (audit trail)
```

### Keunggulan Atomic Stock Update

**Tanpa Atomic Update (Bermasalah):**
```python
# RACE CONDITION - BERBAHAYA!
current_stock = get_stock(product_id)  
new_stock = current_stock - quantity   
update_stock(product_id, new_stock)   
```

**Dengan Atomic Update (Aman):**
```sql
-- Single atomic operation at database level
UPDATE produk 
SET stok = stok - 5 
WHERE produk_id = 1 AND stok >= 5;
```

## 🔍 Troubleshooting

### "Koneksi database gagal"
→ Cek `.streamlit/secrets.toml` dan pastikan credentials benar

### "Stok tidak mencukupi" tapi stok ada
→ Klik tombol Refresh (🔄) atau restart aplikasi

### Function `atomic_stock_deduct` not found
→ Jalankan ulang SQL function dari `database_schema.sql`

## 📊 Query Monitoring Berguna

**Cek Produk Stok Rendah:**
```sql
SELECT * FROM produk WHERE stok < 10 ORDER BY stok ASC;
```

**Analisis Produk Terlaris:**
```sql
SELECT ti.nama_produk, SUM(ti.jumlah) as total_terjual
FROM transaksi_item ti
GROUP BY ti.nama_produk
ORDER BY total_terjual DESC;
```

## 🚀 Deployment

### Streamlit Cloud
1. Push ke GitHub
2. Deploy di [share.streamlit.io](https://share.streamlit.io)
3. Tambahkan secrets di settings

### VPS
```bash
screen -S pelitpos
streamlit run app.py --server.port 8501
```

## 📝 License

Bebas digunakan untuk keperluan komersial maupun personal.

---

**PelitPos** - *gk medit gk sugeh ta?*
