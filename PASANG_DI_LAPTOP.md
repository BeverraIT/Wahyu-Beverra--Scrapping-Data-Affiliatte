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

### A2. Akses — tidak perlu diapa-apakan

Repo ini **publik**, jadi orang kantor bisa langsung `git clone` tanpa akun
GitHub, tanpa undangan, dan tanpa diminta login.

> Konsekuensinya yang sudah disepakati: nama 7 toko, `shop_id`, dan kode
> produk bisa dilihat siapa saja. Data creator, cookie login, dan file Excel
> **tidak** ikut — semuanya di luar git sejak awal.

### A3. Catat yang perlu dibawa

Siapkan di catatan HP, akan dipakai di tiap laptop:

- Alamat repo:
  `https://github.com/BeverraIT/Wahyu-Beverra--Scrapping-Data-Affiliatte.git`
- Username + password akun toko yang akan dipegang orang itu

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

Ada dua cara. **Cara 1 jauh lebih cepat** — coba itu dulu.

#### Cara 1: satu perintah (Windows 10/11 yang agak baru)

1. Tekan tombol **Windows**, ketik `cmd`, lalu tekan Enter
2. Ketik ini (boleh copy-paste, klik kanan di jendela hitam untuk paste):

   ```
   winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
   ```

3. Enter, lalu tunggu sampai muncul tulisan **Successfully installed**
4. **Tutup jendela Command Prompt-nya, buka lagi yang baru.**

   Ini wajib. Kalau tidak, `git` masih dianggap belum ada karena jendela lama
   belum tahu ada program baru.

Kalau muncul `'winget' is not recognized`, berarti Windows-nya terlalu lama —
pakai Cara 2.

#### Cara 2: unduh manual

1. Buka <https://git-scm.com/download/win>
2. Klik **64-bit Git for Windows Setup**, tunggu unduhannya
3. Jalankan file-nya. Akan muncul **belasan layar** — klik **Next** terus,
   kecuali dua layar ini:

   | Layar | Yang harus dipastikan |
   |---|---|
   | **"Choosing the default editor used by Git"** | Ganti dari `Vim` jadi **`Use Notepad as Git's default editor`**. Vim susah dipakai kalau belum terbiasa — bisa nyangkut tidak bisa keluar |
   | **"Adjusting your PATH environment"** | Pilih yang **tengah**: *Git from the command line and also from 3rd-party software*. Ini pilihan bawaannya, jangan diubah — kalau salah, `Jalankan.bat` tidak akan menemukan git |

   Sisanya biarkan apa adanya, termasuk layar *"Configuring the line ending
   conversions"* — aplikasi ini sudah mengurus sendiri lewat `.gitattributes`.

4. Klik **Install**, tunggu, lalu **Finish**
5. **Tutup Command Prompt yang sedang terbuka, buka lagi yang baru**

#### Memastikan berhasil

Di Command Prompt **yang baru dibuka**, ketik:

```
git --version
```

Harus muncul seperti `git version 2.52.0.windows.1`.

Kalau muncul `'git' is not recognized`, coba tutup-buka Command Prompt sekali
lagi. Kalau masih, ulangi Cara 2 dan periksa layar **PATH** tadi.

### B4. Ambil aplikasinya

Masih di Command Prompt, ketik satu per satu (Enter tiap baris):

```
cd /d C:\
mkdir Aplikasi
cd Aplikasi
git clone https://github.com/BeverraIT/Wahyu-Beverra--Scrapping-Data-Affiliatte.git TarikCreator
```

Tidak akan diminta login — repo-nya publik.

Hasilnya folder `C:\Aplikasi\TarikCreator`.

> Kalau `mkdir Aplikasi` bilang sudah ada, abaikan saja, lanjut.

> ### JANGAN pakai tombol "Download ZIP"
>
> Di halaman GitHub ada tombol hijau **Code** → **Download ZIP**. **Jangan
> dipakai.** Hasilnya folder berakhiran `-master` yang tidak bisa diperbarui
> sama sekali — `Perbarui.bat` tidak akan jalan, dan tiap ada perbaikan harus
> unduh ulang manual.
>
> Harus `git clone` seperti perintah di atas. Bedanya tidak kelihatan dari isi
> foldernya, tapi menentukan bisa-tidaknya di-update.
>
> Sudah terlanjur pakai ZIP? Hapus foldernya, lalu ulangi `git clone`. Tidak
> ada yang hilang — sesi login tersimpan terpisah di luar folder aplikasi.

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

> **Kalau Chrome laptop itu sudah login ke tokonya**, lewati langkah di bawah:
> tutup semua jendela Chrome, centang tokonya, lalu klik
> **Ambil Login dari Chrome**. Sesinya langsung dipindah, tidak perlu login
> dua kali. Toko yang tidak terbukti login akan dilewati — itu tetap harus
> login manual seperti di bawah.

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
| `'git' is not recognized` | Git belum terpasang, ATAU Command Prompt-nya belum ditutup-buka setelah memasang | Tutup semua Command Prompt, buka baru. Kalau masih, ulangi B3 |
| `'winget' is not recognized` | Windows-nya terlalu lama untuk cara cepat | Pakai Cara 2 di langkah B3 |
| Jendela CMD hilang cepat, tidak ada aplikasi | Kemungkinan file `.bat` rusak | Di folder aplikasi jalankan `python cek_bat.py` |
| `ModuleNotFoundError` | Dibuka lewat `gui.py`, bukan `Jalankan.bat` | Tutup, klik `Jalankan.bat` |
| "Google Chrome tidak ketemu" | Chrome belum terpasang | Ulangi langkah B1 |
| Antivirus kantor memblokir `.bat` | Kebijakan kantor | Minta IT mengizinkan folder `C:\Aplikasi\TarikCreator` |
| Nama folder berakhiran `-master` | Diambil lewat Download ZIP, bukan `git clone` | Hapus foldernya, ulangi langkah B4 |
| `Perbarui.bat` bilang "bukan hasil git clone" | Sama seperti di atas | Hapus foldernya, ulangi langkah B4 |
| Menjalankan `siapkan_profil.py` | File itu sudah dihapus, tidak dipakai lagi | Pakai **Login Toko** di aplikasi |

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
