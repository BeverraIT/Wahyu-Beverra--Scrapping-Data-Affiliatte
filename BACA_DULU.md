# Tarik Creator Affiliate — cara pakai

Aplikasi untuk mengambil **top 10 produk × 50 creator** dari Affiliate Center,
langsung jadi Excel yang tinggal di-copy ke sheet AFFILIATE 3.

Panduan ini untuk pemakai. Yang teknis ada di `PANDUAN.md`.

---

## Pertama kali di komputer baru

### 1. Pasang Python (sekali seumur hidup)

Kalau belum ada, unduh dari <https://www.python.org/downloads/>.

> **Penting:** waktu memasang, centang **"Add Python to PATH"** di layar
> pertama. Kalau lupa, aplikasinya tidak akan bisa dibuka.

Chrome juga harus sudah terpasang.

### 2. Salin folder aplikasi

Copy folder ini ke komputermu, taruh di mana saja yang gampang dicari
(misalnya `D:\Aplikasi\TarikCreator`).

**Yang perlu ikut disalin:**

```
Jalankan.bat        BACA_DULU.md        toko.json
*.py  (semua file Python)
```

**Yang JANGAN ikut disalin** — ini punya komputer asalnya, dan kalau ikut
terbawa malah bikin error:

```
__pycache__\        hasil\        logs\        debug_screenshots\
```

> Jangan menyalin folder profil login dari komputer orang lain. Tiap orang
> login sendiri lewat aplikasi — itu bagian dari langkah berikutnya.

### 3. Buka aplikasinya

Klik dua kali **`Jalankan.bat`**.

Pertama kali dibuka akan agak lama (sedang menyiapkan kebutuhannya).
Berikutnya langsung terbuka.

### 4. Login toko

Di daftar toko, tiap baris ada tombol **Login Toko**.

1. Klik **Login Toko** di toko yang mau kamu pakai
2. Chrome terbuka di halaman Affiliate Center
3. Login seperti biasa
4. **Jendelanya akan menutup sendiri** kalau sudah berhasil — tidak perlu
   klik apa-apa lagi di aplikasi

Cukup sekali. Sesinya tersimpan, besok-besok tinggal pakai.

Ulangi untuk tiap toko yang jadi tanggung jawabmu. Toko yang tidak kamu
pegang boleh dibiarkan tidak login.

---

## Pemakaian sehari-hari

1. Buka **`Jalankan.bat`**
2. Pilih **Bulan** dan **Tahun** (bawaannya bulan penuh terakhir — biasanya
   sudah benar)
3. **Centang** toko yang mau ditarik
4. Klik **Tarik Data + Buat Excel**
5. Tunggu. Satu toko sekitar **2–3 menit**, jadi 6 toko sekitar 15 menit
6. Klik **Buka Folder Hasil**

Chrome akan terbuka-tutup sendiri selama proses. **Jangan ditutup atau
diklik-klik** — biarkan saja sampai selesai. Kamu tetap bisa memakai Chrome
biasamu untuk kerja lain; aplikasi ini memakai jendela Chrome-nya sendiri.

Kolom **Catatan** di bawah menunjukkan apa yang sedang dikerjakan. Kalau ada
yang gagal, alasannya muncul di situ dengan tulisan merah.

### Hasilnya

Satu file Excel per toko, di folder `hasil/`:

```
TOP50_CREATOR_Yarra_Store_Agustus_2026.xlsx
```

Isinya:

| Sheet | Gunanya |
|---|---|
| **SIAP_PASTE** | 500 baris, susunannya persis AFFILIATE 3. Blok-copy langsung |
| **RINGKASAN** | Cek cepat: produk mana yang creator-nya kurang dari 50 (merah) |
| **01–10** | Detail per produk, lebih lengkap termasuk Creator ID |

---

## Kalau ada masalah

| Yang terjadi | Artinya | Yang harus dilakukan |
|---|---|---|
| Baris toko merah **"BELUM LOGIN"** | Sesi login sudah habis | Klik **Login Toko** lagi |
| **"BELUM DISIAPKAN"** | Belum pernah login di komputer ini | Klik **Login Toko** |
| **"TIDAK ADA DATA"** | Halaman terlalu lama memuat | Klik **Cek** lagi. Kalau masih, cek koneksi internet |
| Jumlah creator kurang dari 50 | Toko itu memang creator-nya sedikit bulan itu | Normal, tidak perlu diapa-apakan |
| Aplikasi tidak mau terbuka | Python belum terpasang / lupa "Add to PATH" | Pasang ulang Python, centang **Add Python to PATH** |
| `ModuleNotFoundError: No module named 'requests'` | Aplikasi dibuka langsung lewat `gui.py`, bukan `Jalankan.bat` | Tutup, lalu klik **`Jalankan.bat`** — batch itu yang memasang kebutuhannya |
| "Google Chrome tidak ketemu" | Chrome belum terpasang | Pasang dari <https://www.google.com/chrome/> |

Kalau tetap buntu, kirim isi kolom **Catatan** — di situ alasannya tertulis.
Log lengkap juga tersimpan di folder `logs/`.

---

## Menambah toko baru

1. Buka Affiliate Center toko itu di Chrome
2. Lihat alamatnya, salin angka setelah `shop_id=`

   ```
   https://affiliate-id.tokopedia.com/data/product-performance?shop_region=ID&shop_id=7494510375204653632
                                                                                      ^^^^^^^^^^^^^^^^^^^
   ```
3. Di aplikasi, klik **Tambah Toko**, isi namanya dan angka tadi
4. Klik **Login Toko** di baris yang baru muncul

Toko yang ditambahkan tersimpan di `toko.json`. Kalau ingin semua orang
kantor ikut punya toko itu, bagikan file `toko.json`-nya — isinya cuma nama
dan shop_id, **bukan** data login.

---

## Yang perlu diketahui

- **Data login tidak ikut tersalin.** Sesi loginmu disimpan terpisah di
  `%LOCALAPPDATA%\TarikCreatorAffiliate`, tidak di folder aplikasi. Jadi
  aman kalau folder aplikasinya dibagikan.
- **Aplikasi ini hanya membaca.** Tidak mengubah apa pun di Affiliate Center,
  cuma membuka halaman dan mencatat angkanya.
- Kolom **"Pesanan"** tidak ada di Excel karena Affiliate Center memang tidak
  mengirim jumlah pesanan per creator — yang ada hanya "Items sold".
