# Memasang di laptop orang kantor

Ikuti dari atas ke bawah. Sekitar **20–30 menit** per laptop, sebagian besar
cuma menunggu unduhan.

---

## BAGIAN A — Yang kamu siapkan sekali saja (di komputermu)

Cukup dilakukan **satu kali**, bukan per laptop.

### A1. Kirim kode terbaru ke GitHub

Di folder aplikasi, buka Command Prompt lalu ketik:

```
git push origin master
```

Kalau diminta login, pakai akun GitHub-mu (`BeverraIT`).

> Tanpa langkah ini, laptop kantor akan mengambil versi lama yang masih ada
> bug-nya.

### A2. Beri akses ke orang kantor

Kalau repo-nya **privat**, tiap orang harus kamu daftarkan dulu:

1. Buka <https://github.com/BeverraIT/Wahyu-Beverra--Scrapping-Data-Affiliatte>
2. Klik tab **Settings** → menu kiri **Collaborators**
3. Klik **Add people**, masukkan username GitHub orang itu
4. Orang itu akan dapat email undangan — **harus diterima dulu** sebelum bisa
   `git clone`

Kalau tidak mau repot dengan akun GitHub per orang, alternatifnya jadikan repo
**publik**. Tapi ingat: `toko.json` (nama toko + shop_id) jadi bisa dilihat
siapa saja. Itu bukan password dan tidak bisa dipakai masuk ke mana-mana, tapi
membocorkan toko mana saja yang kalian kelola.

### A3. Catat yang perlu dibawa

Siapkan di catatan HP, akan dipakai di tiap laptop:

- Alamat repo:
  `https://github.com/BeverraIT/Wahyu-Beverra--Scrapping-Data-Affiliatte.git`
- Username + password akun toko yang akan dipegang orang itu
- Username GitHub orang itu (kalau repo privat)

---

## BAGIAN B — Di tiap laptop orang kantor

### B1. Pasang Google Chrome

Cek dulu: sudah ada Chrome? Kalau sudah, lewati.

Kalau belum: <https://www.google.com/chrome/> → **Download** → jalankan.

### B2. Pasang Python

1. Buka <https://www.python.org/downloads/>
2. Klik tombol kuning besar **Download Python 3.x**
3. Jalankan file yang terunduh
4. **BERHENTI SEBENTAR DI LAYAR PERTAMA.**

   Ada kotak centang di bawah: **"Add python.exe to PATH"**.
   **CENTANG DULU** kotak itu, baru klik **Install Now**.

   Kalau lupa dicentang, aplikasinya tidak akan bisa dibuka sama sekali dan
   harus pasang ulang.

5. Tunggu sampai selesai, klik **Close**

**Cara memastikan berhasil:** tekan tombol Windows, ketik `cmd`, Enter. Lalu
ketik:

```
python --version
```

Harus muncul tulisan seperti `Python 3.13.7`. Kalau muncul
`'python' is not recognized`, berarti "Add to PATH" tadi terlewat — pasang
ulang Python-nya.

### B3. Pasang Git

1. Buka <https://git-scm.com/download/win>
2. Klik **64-bit Git for Windows Setup**
3. Jalankan, lalu klik **Next** terus sampai **Install**

   Semua pilihan bawaannya sudah benar, tidak ada yang perlu diubah.

**Cara memastikan berhasil:** di Command Prompt ketik:

```
git --version
```

Harus muncul seperti `git version 2.xx.x`.

### B4. Ambil aplikasinya

Masih di Command Prompt, ketik satu per satu (Enter tiap baris):

```
cd /d C:\
mkdir Aplikasi
cd Aplikasi
git clone https://github.com/BeverraIT/Wahyu-Beverra--Scrapping-Data-Affiliatte.git TarikCreator
```

Kalau muncul jendela minta login GitHub, isi dengan akun orang itu (yang sudah
kamu undang di langkah A2).

Hasilnya folder `C:\Aplikasi\TarikCreator`.

> Kalau `mkdir Aplikasi` bilang sudah ada, abaikan saja, lanjut.

### B5. Buka aplikasinya

1. Buka folder `C:\Aplikasi\TarikCreator`
2. Klik dua kali **`Jalankan.bat`**
3. Pertama kali akan muncul tulisan "Menyiapkan aplikasi..." dan proses
   unduhan — **tunggu**, ini cuma sekali. Sekitar 1–2 menit.
4. Jendela aplikasi akan terbuka

Kalau Windows memunculkan peringatan "Windows protected your PC", klik
**More info** → **Run anyway**. Itu muncul karena file-nya baru, bukan karena
berbahaya.

### B6. Login toko

Di jendela aplikasi:

1. Klik **Login Toko** di baris toko yang jadi tanggung jawab orang itu
2. Chrome terbuka di halaman Affiliate Center
3. Login pakai akun toko tersebut
4. **Jendela Chrome menutup sendiri** kalau berhasil — tidak perlu klik apa pun
   di aplikasi

Ulangi untuk tiap toko yang dia pegang. Toko yang tidak dia pegang biarkan
saja.

### B7. Uji sekali

1. Centang **satu** toko saja dulu (biar cepat kelihatan hasilnya)
2. Pastikan Bulan dan Tahun sudah benar
3. Klik **Tarik Data + Buat Excel**
4. Tunggu 2–3 menit. Chrome akan buka-tutup sendiri — **jangan disentuh**
5. Klik **Buka Folder Hasil** — harus ada file Excel di situ

Kalau file Excel-nya ada dan isinya benar, laptop itu sudah beres.

---

## Kalau ada yang gagal

| Yang muncul | Artinya | Yang dilakukan |
|---|---|---|
| `'python' is not recognized` | "Add to PATH" terlewat waktu memasang | Pasang ulang Python, centang kotak itu |
| `'git' is not recognized` | Git belum terpasang | Ulangi langkah B3 |
| Jendela CMD hilang cepat, tidak ada aplikasi | Kemungkinan file `.bat` rusak | Di folder aplikasi jalankan `python cek_bat.py` |
| `ModuleNotFoundError` | Dibuka lewat `gui.py`, bukan `Jalankan.bat` | Tutup, klik `Jalankan.bat` |
| "Google Chrome tidak ketemu" | Chrome belum terpasang | Ulangi langkah B1 |
| Minta login GitHub terus | Orangnya belum diundang / belum terima undangan | Ulangi langkah A2 |
| Antivirus kantor memblokir `.bat` | Kebijakan kantor | Minta IT mengizinkan folder `C:\Aplikasi\TarikCreator` |

---

## Setelah semua terpasang

Kalau nanti ada perbaikan aplikasi, kamu cukup:

```
git add -A
git commit -m "keterangan perbaikan"
git push origin master
```

Orang kantor tinggal klik **`Perbarui.bat`**. Tidak perlu kirim file lagi
selamanya.
