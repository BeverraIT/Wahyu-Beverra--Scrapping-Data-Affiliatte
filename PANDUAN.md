# Tarik Creator Affiliate

Ambil top 10 produk dari Affiliate Center → 50 creator per produk → Excel 500 baris siap paste ke **AFFILIATE 3**.

**Pemakai cukup baca [BACA_DULU.md](BACA_DULU.md).** File ini untuk yang merawat kodenya.

## Pasang sekali

`Jalankan.bat` sudah mengurus ini sendiri waktu pertama dibuka. Manual:

```
pip install websocket-client requests openpyxl
```

Butuh Python 3.9+ (dengan tkinter, bawaan installer resmi) dan Chrome.

## Bentuk aplikasi

```
Jalankan.bat        <- yang diklik orang kantor: cek Python, pasang kebutuhan, buka GUI
gui.py              <- jendela aplikasi (tkinter, bawaan Python)
akun.py             <- login toko + cek status (dipakai GUI dan cek_toko.py)
lokasi.py           <- semua path dihitung saat jalan, tidak ada path komputer tertentu
toko.json           <- daftar toko kantor (nama, shop_id, slug, port). Boleh dibagikan
konfigurasi.py      <- ambang, selektor, pemetaan kolom; TOKO dibaca dari toko.json
mesin_cdp.py        <- Chrome + DevTools Protocol
tarik_creator.py    <- alur penarikan
generate_excel.py   <- perakitan Excel
impor_profil.py     <- SEKALI: pindahkan sesi login dari Chrome lama
Menu_Lanjutan.bat   <- menu terminal lama (rekam endpoint, rakit dari rekaman, dll)
```

### Yang membuat aplikasi ini bisa dipakai orang lain

Sebelumnya semua bergantung pada `C:\Users\User\ChromeToko\...` — path khusus
satu komputer. Sekarang:

| | Di mana | Kenapa di situ |
|---|---|---|
| Profil Chrome | `%LOCALAPPDATA%\TarikCreatorAffiliate\profil\<slug>` | Ratusan MB dan berisi sesi login pribadi. **Tidak boleh** ikut tersalin waktu folder aplikasi dibagikan. |
| Hasil, log, `toko.json` | di sebelah aplikasi | Gampang dicari. Kalau foldernya tidak boleh ditulisi (mis. Program Files), otomatis pindah ke Documents. |
| Centang toko + periode | `%LOCALAPPDATA%\...\setelan.json` | Pilihan pribadi tiap orang, tidak ikut dibagikan. |

Profil Chrome milik aplikasi **selalu** memakai `--profile-directory=Default`.
Tidak lagi menumpang profil Chrome orang, jadi tidak ada lagi urusan "login-nya
di folder `Yarra Store` atau `Default`?" yang dulu bikin Moonklaz gagal.

### Login

Tombol **Login Toko** membuka Chrome dengan profil aplikasi ke halaman
Affiliate Center. Selesainya **dideteksi sendiri**: bukan dari orang menekan
tombol, tapi dari `product/list` yang akhirnya menjawab. Jadi tidak ada
tebak-tebakan kapan login beres.

### Aturan thread di GUI

Dua hal yang wajib dijaga kalau menyentuh `gui.py`:

1. Semua kerja berat jalan di thread terpisah. Kalau tidak, jendelanya membeku
   dan orang mengira aplikasinya hang.
2. Thread **tidak boleh** menyentuh widget tkinter. Semua kabar dikirim lewat
   `self.antrean`, dibaca jendela tiap 100 ms. Menyentuh widget dari thread
   lain bikin crash yang susah dilacak karena munculnya acak.

`tarik_creator` punya tiga kait untuk ini: `PENCATAT` (log dialihkan ke
jendela), `BERHENTI` (tombol Hentikan), dan `INTERAKTIF=False` — GUI **wajib**
mematikannya karena tidak ada terminal untuk menjawab `input()`.

### Pindah dari susunan lama

Sekali saja, di komputer yang sudah punya profil login lama:

```
python impor_profil.py --dari "C:\Users\User\ChromeToko"
```

Untuk tiap toko dicari folder dengan cookie **sesi** (`seller-id` +
`affiliate-id`) terbanyak, lalu disalin jadi `Default` di profil aplikasi.
Sengaja bukan "cookie tokopedia terbanyak" — folder `Default` biasanya menang
di hitungan itu karena penuh cookie iklan, padahal justru bukan yang login.

Periode default = **bulan penuh terakhir**. Mau bulan lain, isi `PERIODE_MANUAL = (2026, 8)`.

## Urutan pakai

Orang kantor cukup klik `Jalankan.bat`. Yang di bawah untuk lewat terminal:

| Langkah | Perintah | Kapan |
|---|---|---|
| 0 | `python impor_profil.py --dari <folder>` | sekali, hanya kalau pindah dari susunan lama |
| 0b | `python cek_toko.py` | sebelum menarik -- 15-60 detik per toko |
| 1 | `python rekam_endpoint.py` | hanya kalau tampilan Affiliate Center berubah |
| 2 | `python tarik_creator.py` | tarik data bulanan, semua toko yang dicentang |
| 2b | `python dari_rekaman.py` | ganti langkah 2 kalau otomatisasi macet |
| 3 | `python generate_excel.py` | setelah langkah 2 atau 2b, satu Excel per toko |

Atau lewat `Menu_Lanjutan.bat`.

### Kenapa harus rekam dulu

Halaman Affiliate Center ambil datanya lewat XHR JSON. Nama endpoint dan nama field-nya cuma bisa dipastikan dari halaman aslinya. `rekam_endpoint.py` membuka Chrome dengan profil toko, kamu klik manual sekali (analitik produk → periode 1 bulan → detail produk top 1 → daftar creator), lalu semua response tersimpan di `hasil/rekaman_endpoint.json` plus ringkasan strukturnya dicetak di layar.

Dari situ dua hal dikunci:
1. **Pola URL endpoint** → isi ke `POLA_API` di konfigurasi
2. **Nama field asli** → cocokkan ke `PETA_KOLOM` (mis. kalau ternyata GMV bernama `gmv_amt`, tambahkan ke daftar)

Setelah dua itu terisi, langkah 2 jalan otomatis penuh tanpa klik.

> **Jendela Chrome tidak kelihatan saat merekam?** Selain `OFFSCREEN = False`, Chrome
> juga mengingat posisi jendela terakhir di dalam profil (`browser.window_placement`).
> Bekas run offscreen bikin jendela dibuka di koordinat -21845,-21845, di luar layar.
> Sekarang posisinya dipaksa ulang lewat `JENDELA_POSISI` / `JENDELA_UKURAN` di konfigurasi:
> flag `--window-position`, patch Preferences, dan `Browser.setWindowBounds` sekaligus.
> Ini cuma berlaku waktu mesin menjalankan Chrome sendiri. Kalau Chrome toko sudah jalan,
> mesin menumpang ke situ dan jendelamu tidak digeser sama sekali — tinggal lihat tab baru
> yang muncul. Sebaliknya, kalau mesin gagal menyambung padahal Chrome toko jalan tanpa
> `--remote-debugging-port`, tutup dulu Chrome itu: dua Chrome dengan `--user-data-dir`
> sama tidak bisa jalan barengan, dan port CDP-nya tidak akan hidup.

## Hasil

```
hasil/
├── mentah/Yarra_Store_2026-08.json        <- data mentah, arsip
└── TOP50_CREATOR_Yarra_Store_Agustus_2026.xlsx
```

Isi Excel:
- **RINGKASAN** — cek cepat, produk mana yang creator-nya kurang dari 50 (ditandai merah)
- **SIAP_PASTE** — 500 baris, blok-copy langsung ke tab toko + bulan di AFFILIATE 3
- **01–10** — detail per produk

Susunan sheet SIAP_PASTE diatur lewat `KOLOM_SIAP_PASTE` di `konfigurasi.py` --
sudah dicocokkan persis dengan header AFFILIATE 3 (16 kolom A-P). Kode pendek
kolom "Produk Top 10" diisi di `KODE_PRODUK`; yang belum diisi ditebak dari
kata terakhir nama produk dan selalu dilaporkan waktu Excel dibuat.

## Browser di latar belakang

`TAMPILKAN_BROWSER = False` (bawaan) menjalankan Chrome dengan
`--headless=new`: halamannya tetap dirender penuh, cuma tidak ditampilkan.

**Jangan menggantinya dengan memindahkan jendela ke luar layar.** Sudah
diuji dan gagal: dengan `OFFSCREEN = True`, Affiliate Center tidak menarik
data sama sekali (0 produk setelah 35 detik untuk semua toko) karena Chrome
menahan halaman yang dianggap tidak terlihat. Headless beda -- halamannya
tetap dirender.

### Terukur: headless justru LEBIH andal

Diuji dengan halaman yang menghitung `requestAnimationFrame`,
`IntersectionObserver`, dan `setInterval` selama 6 detik:

| Mode | rAF | IntersectionObserver | setInterval |
|---|---|---|---|
| tampil, tertutup jendela lain | 1 | 0 | 8 |
| di luar layar | 1 | 0 | 8 |
| **headless** | **483** | **1** | **80** |

Jendela yang "tampil" pun ikut ditahan Chrome kalau tertutup jendela lain --
sama seperti yang di luar layar. Itu persis mekanisme yang dipakai tabel
Affiliate Center untuk memuat data. Jadi headless bukan cuma sama baiknya,
tapi lebih andal daripada jendela tampil yang bisa tertimpa.

### User-Agent headless disamarkan

Headless mengaku `HeadlessChrome/152.0.0.0` di User-Agent. Situs seperti
Tokopedia bisa memperlakukannya beda, dan gejalanya bakal membingungkan:
jalan waktu ditampilkan, gagal waktu di latar belakang. `_samarkan_headless()`
menggantinya jadi `Chrome/...` lewat `Network.setUserAgentOverride`, versinya
diambil dari UA yang ada supaya ikut terbarui sendiri.

Tiga tempat memaksa `tampil=True` karena butuh orangnya melihat/mengetik:

| Tempat | Alasan |
|---|---|
| `akun.login()` | orangnya mengetik akun dan sandi |
| `rekam_endpoint.py` | seluruh gunanya adalah kamu mengklik sendiri |
| Sakelar di GUI | kalau orangnya memang ingin melihat prosesnya |

Jendela yang ditampilkan ditaruh di **tengah layar** (`posisi_jendela()`
menghitung dari `GetSystemMetrics`), bukan di pojok -- supaya waktu login
Chrome-nya langsung kelihatan dan tidak perlu dicari atau digeser.

## Tab menumpuk tiap kali dijalankan

Gejalanya: tiap run tabnya nambah, lama-lama Chrome penuh tab. Dua sebabnya:

1. **`--restore-last-session=false` justru MENYALAKAN pemulihan sesi.**
   Chrome memeriksa flag ini dengan `HasSwitch()`, jadi nilainya diabaikan --
   yang dilihat cuma flag-nya ada atau tidak. Menulis `=false` tetap dibaca
   "pulihkan sesi lama". Flag itu sudah dibuang; pengaturannya sekarang di
   Preferences (`session.restore_on_startup = 5`).

2. **Situsnya membuka tab sendiri.** Sesudah login, Tokopedia kadang membuka
   Affiliate Center di tab baru. Tab itu bukan buatan kita jadi tidak pernah
   ditutup. `_tutup_tab_sisa()` membersihkannya di AWAL run berikutnya --
   sengaja di awal, bukan di tengah, supaya tidak menutup tab yang sedang
   dipakai orang untuk login.

`tutup()` juga memakai `Browser.close` (tutup baik-baik) sebelum jatuh ke
`terminate()`. `terminate()` itu kill mendadak: Chrome menganggapnya crash.

Terukur sesudah diperbaiki: tiga run berturut-turut, tiap run mulai dengan
1 tab walau run sebelumnya berakhir dengan 3.

## Popup pengumuman & peringatan halaman ditutup

Affiliate Center kadang memunculkan modal pengumuman. Selama modalnya
terbuka, klik apa pun di belakangnya TIDAK tembus -- otomatisasi macet tanpa
sebab yang kelihatan. `tutup_popup()` dipanggil di empat titik: sesudah
halaman termuat, sebelum klik baris produk, sesudah detail terbuka, dan saat
klik halaman creator gagal.

Dua hal yang bikin fungsi itu benar:

- **Jangan pakai `offsetParent` untuk cek terlihat.** Elemen `position:fixed`
  -- yaitu semua modal -- selalu memberi `null`, jadi popupnya tidak pernah
  ketemu. Versi pertama kena ini dan ujinya melaporkan `ditutup=0`. Sekarang
  dipakai `getBoundingClientRect()` + `getComputedStyle`.
- **Tombolnya dicari HANYA di dalam modal, teksnya dicocokkan persis.**
  Halaman punya tombol lain bernama "Oke"/"Tutup"; kalau dicocokkan dengan
  "mengandung" atau dicari di seluruh halaman, tombol yang salah bisa
  terpencet. Diuji: tombol "Oke" kembar di luar modal tidak tersentuh, dan
  halaman tanpa modal menghasilkan nol klik.

### Halaman ini akan dinonaktifkan Tokopedia

Bannernya sudah muncul: *"Halaman ini akan segera dinonaktifkan. Sementara
itu, data bisa Anda akses di halaman Performa baru."*

`periksa_peringatan_halaman()` mendeteksi kalimat itu dan menulisnya ke log
tiap penarikan, jadi tidak akan kaget waktu halamannya benar-benar mati.
Kalau sudah mati, alur pemulihannya sudah ada: `rekam_endpoint.py` di halaman
Performa yang baru, lalu kunci ulang `POLA_API` + `PETA_KOLOM` + selektornya
seperti waktu pertama kali dibangun.

## Kenapa sesi Chrome tidak bisa disalin

Chrome sejak v127 mengenkripsi cookie dengan App-Bound Encryption: nilai
cookie berawalan `v20` dan kuncinya ada di `Local State` sebagai
`os_crypt.app_bound_encrypted_key`, terikat ke aplikasi Chrome-nya. Cookie
begitu **sengaja** tidak bisa dibaca kalau filenya disalin ke folder lain --
memang itu tujuannya, mencegah pencurian sesi.

Terukur di komputer ini:

| Sumber | `app_bound_key` | Versi cookie | Bisa disalin? |
|---|---|---|---|
| Chrome sehari-hari | ADA | `v20` | tidak |
| Profil lama `ChromeToko` | - | `v10` | ya |

Makanya `impor_profil.py` berhasil untuk profil `ChromeToko` tapi gagal untuk
Chrome biasa. Yang berbahaya: menyalinnya tetap "berhasil" tanpa error, lalu
profilnya kelihatan punya cookie padahal tidak bisa login. Jadi `v20`
dideteksi SEBELUM menyalin dan ditolak dengan alasan yang jelas.

Jalan keluar lain sudah dipertimbangkan dan buntu: menyetir profil Chrome
asli lewat CDP juga diblokir Chrome (sejak v136 `--remote-debugging-port`
diabaikan untuk user-data-dir bawaan, alasan yang sama). Dua pengaman itu
bekerja bersamaan, dan memang begitu rancangannya.

Kesimpulannya: untuk Chrome modern, **login sekali lewat tombol Login Toko**
adalah satu-satunya cara -- dan itu cukup sekali seumur pemakaian.

## Pelajaran soal file .bat

Dua kali kena, keduanya gejalanya "jendela CMD hilang begitu saja":

- **File `.bat` WAJIB CRLF.** `Jalankan.bat` sempat tersimpan dengan akhir baris
  LF saja. `cmd.exe` salah membaca blok `if (...)` bertingkat, sebagian perintah
  jalan (pip sempat mengunduh) lalu sisanya tertelan dan jendelanya tutup tanpa
  pesan apa pun. Cek cepat:

  ```
  python cek_bat.py
  ```

  Kalau ada file yang dilaporkan LF, file itu rusak untuk cmd -- buka di
  Notepad++ / VS Code, ganti akhir barisnya ke CRLF, simpan.

  Struktur `label + goto` dipakai sekarang karena jauh lebih tahan daripada
  `if (...)` bertingkat, yang paling gampang salah baca kalau akhir barisnya keliru.

- **Jangan pakai file penanda "sudah terpasang".** Versi pertama membuat file
  `.siap` setelah pip berhasil. File itu ikut tersalin waktu folder aplikasi
  dibagikan, jadi di PC kantor pemasangan dilewati padahal `requests` belum ada
  di sana. Penanda mencatat keadaan komputer ASAL, bukan komputer yang sedang
  dipakai. Sekarang kebutuhannya ditanyakan langsung ke Python:

  ```
  %PY% -c "import requests, websocket, openpyxl" >nul 2>&1
  ```

  (Kalau masih ada file `.siap` tertinggal di folder, boleh dihapus. Sudah
  tidak dipakai.)

## Pelajaran lama yang sudah dipasang di kode

Diambil dari mesin Tarik Omset, jangan diulang lagi sakitnya:

- Klik tanggal **wajib** pakai event mouse asli (`Input.dispatchMouseEvent`). `.click()` dari JS kelihatan berhasil tapi nilainya tidak pernah commit.
- Sukses set tanggal = kalender menutup sendiri **dan** nilai input cocok persis. Bandingkan sebagai angka, bukan substring — "Agt 15" pernah lolos karena mengandung "1".
- Halaman suka mereset tanggal ke hari ini. Setelah set periode, langsung lanjut aksi berikutnya, jangan menyentuh UI lain.
- ~~Jalan headed-tapi-di-luar-layar~~ **TIDAK berlaku di halaman ini.** Sudah diuji:
  dengan `OFFSCREEN = True`, Affiliate Center tidak menarik data sama sekali (0 produk
  setelah 35 detik); dengan jendela kelihatan, langsung dapat. Chrome menahan fetch
  untuk jendela yang dianggap tidak terlihat. Biarkan `OFFSCREEN = False`.
- Chrome butuh `--remote-allow-origins=*` plus patch Preferences supaya balon "Restore pages?" tidak muncul.

## Endpoint & field (sudah dikunci dari rekaman)

Semua di `affiliate-id.tokopedia.com`:

| | |
|---|---|
| Daftar produk | `/api/v2/insights/affiliate_compass/affiliate/seller/product_analytics/product/list` |
| Daftar creator | `/api/v2/insights/affiliate_compass/affiliate/seller/product_analytics/creator/list` |

Bentuk response dua-duanya sama:

```
data.segments[]
  .filter                        -> {"product_id": ..., "seller_id": ...}
  .time_descriptor               -> {"start": "2026-08-01T00:00:00",
                                     "end":   "2026-09-01T00:00:00"}
  .list_control.next_pagination  -> {"has_more":, "next_page":, "total":, "total_page":}
  .timed_lists[].stats[]         -> baris datanya
```

Tiga hal yang gampang menjebak:

1. **`end` itu eksklusif.** Agustus dikirim sebagai `08-01` s/d `09-01`. Validasi periode memakai `time_descriptor`, bukan menebak dari teks halaman — jauh lebih akurat.
2. **Creator itu PAGINASI KLIK, bukan infinite scroll.** 10 baris per halaman, jadi 50 creator = halaman 1 + klik halaman 2,3,4,5 (`li[aria-label="Halaman N"]`). Menggulir tidak memuat apa-apa.
3. **ID itu 19 digit.** `Creator ID` dan `Product ID` ditulis sebagai teks di Excel. Kalau ditulis sebagai angka, Excel memangkasnya di batas 2⁵³ dan digit belakangnya diam-diam jadi nol.

**API tidak mengirim jumlah pesanan (order count) per creator** — yang ada cuma `item_sold_cnt`. Kalau sheet AFFILIATE 3 punya kolom "Pesanan", kosongkan saja; jangan disamakan dengan Item Terjual.

## Kalau otomatisasi macet: rakit dari rekaman

`rekam_endpoint.py` menyimpan SEMUA response yang lewat sementara kamu klik
manual. Kalau klik manualmu sudah melewati 10 produk x 5 halaman creator,
datanya sudah lengkap di situ -- tidak perlu tarik ulang:

```
python dari_rekaman.py
python generate_excel.py
```

Atau menu `[6]` di `Menu_Lanjutan.bat`. Ini jaring pengaman kalau suatu saat
tampilan Affiliate Center berubah dan langkah 2 macet: rekam manual sekali,
Excel-nya tetap jadi.

## Status: otomatis penuh, sudah diverifikasi

Run 2026-09-02 15:15 jalan sendiri dari awal sampai akhir tanpa satu pun prompt
manual: **2 menit 15 detik, 10 produk x 50 creator = 500 baris.**

Hasilnya dibandingkan baris per baris dengan data dari klik manual (rekaman):
**500 dari 500 creator identik, urutannya pun sama.**

Alur klik yang diotomatiskan (design system halaman ini namanya `kora`):

```
input tanggal -> klik tanggal awal -> klik tanggal akhir     (sekali)
  per produk x10:
    "Lihat detailnya" -> Halaman 2,3,4,5 -> tombol "Produk"  (kembali)
```

### Kenapa menunggu, bukan tidur

Semua `sleep` tetap sudah diganti `tunggu_baris()` / `tunggu_tabel_produk()`
yang polling sampai datanya benar-benar datang. Ini bukan kerapian, ini
penyebab kegagalan nyata: run sebelumnya kehilangan 90 baris karena memanen
saat tabel masih berputar memuat.

### Set periode

`set_periode()` mencoba dua cara, sukses selalu diukur dari `time_descriptor`
di response -- bukan dari tampilan:

1. **klik sel kalender** -- ini yang berhasil
2. ketik tanggal ISO di input -- **tidak pernah commit** di UI ini (nilai
   berubah di layar, request tetap pakai periode lama). Ditahan sebagai
   cadangan kalau kalendernya berubah.

Kalau dua-duanya gagal, skrip minta diset manual sekali (matikan dengan
`--otomatis`), dan screenshot-nya masuk ke `debug_screenshots/`.

### Pengaman anti-timpa

Kalau run baru menghasilkan lebih sedikit baris dari file yang sudah ada, file
lama **tidak** ditimpa -- yang baru disimpan sebagai `_parsial.json`. Run
setengah jadi pernah menghapus data 500 baris jadi 410 tanpa peringatan.
