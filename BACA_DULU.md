# Tarik Creator Affiliate — cara pakai

Aplikasi untuk mengambil **top 10 produk × 50 creator** dari Affiliate Center,
langsung jadi Excel yang tinggal di-copy ke sheet AFFILIATE 3.

Panduan ini untuk pemakai sehari-hari.

- Baru mau memasang di laptop baru? Lihat `PASANG_DI_LAPTOP.md`.
- Yang teknis (untuk yang merawat kodenya) ada di `PANDUAN.md`.

---

## Pertama kali di komputer baru

### 1. Pasang Python (sekali seumur hidup)

Kalau belum ada, unduh dari <https://www.python.org/downloads/>.

> **Penting:** waktu memasang, centang **"Add Python to PATH"** di layar
> pertama. Kalau lupa, aplikasinya tidak akan bisa dibuka.

Chrome juga harus sudah terpasang.

### 2. Pasang Git (sekali seumur hidup)

Unduh dari <https://git-scm.com/download/win>. Pilihan bawaannya sudah benar,
tinggal **Next** terus sampai selesai.

Git dipakai supaya aplikasinya bisa diperbarui sendiri — tidak perlu
kirim-kiriman file lagi setiap ada perbaikan.

### 3. Ambil aplikasinya

Buka **Command Prompt**, lalu ketik (ganti `<alamat-repo>` dengan alamat dari
admin):

```
cd /d D:\Aplikasi
git clone <alamat-repo> TarikCreator
cd TarikCreator
```

> **Jangan menyalin folder aplikasi dari komputer orang lain.** Selain
> ketinggalan versi, file-file sisa dari komputer itu bisa bikin error.
> Pakai `git clone`, sekali saja.

Folder profil login juga tidak boleh disalin dari siapa pun — tiap orang
login sendiri lewat aplikasi, itu langkah berikutnya.

### 4. Buka aplikasinya

Klik dua kali **`Jalankan.bat`**.

Pertama kali dibuka akan agak lama (sedang menyiapkan kebutuhannya).
Berikutnya langsung terbuka.

### 5. Login toko

Di daftar toko, tiap baris ada tombol **Login Toko**.

1. Klik **Login Toko** di toko yang mau kamu pakai
2. Chrome terbuka di halaman login Tokopedia
3. Login seperti biasa
4. Kalau setelah login kamu mendarat di **Seller Center** (bukan Affiliate
   Center), **biarkan saja** — aplikasi akan membuka Affiliate Center sendiri
5. **Jendelanya akan menutup sendiri** kalau sudah berhasil — tidak perlu
   klik apa-apa lagi di aplikasi

Cukup sekali. Sesinya tersimpan, besok-besok tinggal pakai.

Ulangi untuk tiap toko yang jadi tanggung jawabmu. Toko yang tidak kamu
pegang boleh dibiarkan tidak login.

#### Sudah login di Chrome biasa? Tidak perlu login dua kali

Kalau di Chrome yang kamu pakai sehari-hari sudah login ke toko itu, sesinya
bisa langsung diambil:

1. **Tutup SEMUA jendela Google Chrome** (wajib, kalau tidak file cookie-nya
   terkunci dan salinannya rusak)
2. Centang toko yang mau diambil
3. Klik **Ambil Login dari Chrome**

Toko hanya diambil kalau riwayat Chrome membuktikan profil itu memang pernah
membuka toko tersebut **dan** sesinya masih hidup. Yang tidak terbukti sengaja
dilewati — lebih baik login sekali lagi daripada salah ambil sesi toko lain
dan datanya tertukar.

Setelah itu klik **Cek Semua** untuk memastikan sesinya benar-benar jalan.

> **Sering kali ini memang tidak bisa, dan itu wajar.** Chrome versi baru
> mengunci cookienya supaya tidak bisa dipindah ke folder lain — pengaman
> anti-pencurian sesi. Kalau muncul pesan *"Chrome versi baru mengunci
> cookienya"*, tidak ada yang salah: klik **Login Toko** dan login sekali.
> Cuma butuh setengah menit, dan cukup sekali seumur pemakaian.

---

## Kalau ada pembaruan aplikasi

Klik **`Perbarui.bat`**. Dia mengambil versi terbaru lalu langsung membuka
aplikasinya. Cukup itu — tidak perlu kirim-kiriman file.

Kalau muncul pesan gagal karena "ada file yang berubah", dan kamu memang tidak
pernah mengedit kodenya, jalankan di Command Prompt dalam folder aplikasi:

```
git restore .
```

lalu klik `Perbarui.bat` lagi.

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
| **RINGKASAN** | Cek cepat + tempat membetulkan **Kode** produk |
| **01–10** | Detail per produk, lebih lengkap termasuk Creator ID |

### Membetulkan kolom "Produk Top 10"

Kode produk (`BSBI`, `TRC`, ...) ditebak dari kata terakhir nama produk, jadi
sering salah — misalnya jadi `TRENDY` atau `KEKINIAN` yang jelas bukan kode.

Betulkannya cukup di **satu tempat**:

1. Buka sheet **RINGKASAN**
2. Betulkan kolom **Kode** (sel kuning). Kolom "Produk Top 10" di SIAP_PASTE
   **ikut berubah sendiri** untuk 50 barisnya
3. Simpan Excel-nya

> Waktu menyalin SIAP_PASTE ke AFFILIATE 3, tempel sebagai **NILAI**
> (klik kanan → Paste Special → Values, atau Ctrl+Shift+V di Google Sheets).
> Kalau ditempel biasa, rumusnya ikut terbawa dan jadi error di sana.

Supaya bulan depan tidak perlu dibetulkan lagi, kirim Excel-nya ke admin —
admin menjalankan `python simpan_kode.py` sekali, dan kodenya tersimpan
untuk semua orang.

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

Toko yang kamu tambahkan tersimpan **di komputermu saja**, sengaja dipisah
supaya `Perbarui.bat` tidak pernah bentrok.

Kalau toko itu perlu dipakai semua orang kantor, kirim nama + shop_id-nya ke
admin. Admin memasukkannya ke daftar bersama, dan yang lain cukup klik
`Perbarui.bat` untuk mendapatkannya.

---

## Yang perlu diketahui

- **Data login tidak ikut tersalin.** Sesi loginmu disimpan terpisah di
  `%LOCALAPPDATA%\TarikCreatorAffiliate`, tidak di folder aplikasi. Jadi
  aman kalau folder aplikasinya dibagikan.
- **Aplikasi ini hanya membaca.** Tidak mengubah apa pun di Affiliate Center,
  cuma membuka halaman dan mencatat angkanya.
- Kolom **"Pesanan"** tidak ada di Excel karena Affiliate Center memang tidak
  mengirim jumlah pesanan per creator — yang ada hanya "Items sold".
