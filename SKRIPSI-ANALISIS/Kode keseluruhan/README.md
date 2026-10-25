# Sistem Analisis Pola Pembelian — Toko Sembiring Sembako
Implementasi skripsi *Perbandingan Apriori dan FP-Growth* (Python + Streamlit + SQLite).

## Menjalankan
```bash
pip install -r requirements.txt
python buat_contoh_data.py      # opsional: membuat contoh_data_transaksi.xlsx (data sintetis)
```
Sebelum menjalankan pertama kali, atur `APP_USER` dan `APP_PASS`; aplikasi tidak menyediakan
kredensial bawaan. Atur juga `APP_RECOVERY` untuk mengaktifkan reset akun. Contoh PowerShell:
```powershell
$env:APP_USER = "pemilik"
$env:APP_PASS = "ganti-dengan-password-kuat"
$env:APP_RECOVERY = "ganti-dengan-kode-pemulihan-kuat"
streamlit run app.py
```
Di Streamlit Cloud, masukkan nilai tersebut pada pengaturan **Secrets**. Jangan unggah file secrets.
Database `sembako.db` dibuat otomatis dan diabaikan oleh Git.

## Struktur file
| File | Isi |
|---|---|
| `app.py` | Semua halaman: Landing Page (Home, Profil Objek, Alamat dan Kontak, Tentang Sistem), Reset Username/Password, Login, Dashboard, Kelola Data, Analisis Algoritma, Perbandingan & Rekomendasi, Riwayat Analisis, Ekspor Laporan, Logout |
| `database.py` | 4 tabel sesuai Bab 4.2.5: `users`, `transactions`, `analysis_results`, `comparison_recommendations` |
| `preprocessing.py` | Pembersihan, standarisasi nama produk (`ALIAS`), hapus transaksi 1 produk, one-hot encoding (di memori) |
| `mining.py` | Apriori & FP-Growth (Mlxtend), Header Table, **FP-Tree**, **Conditional Pattern Base**, rekomendasi bisnis |
| `report.py` | Tabel perbandingan + ekspor Excel (Pandas/Openpyxl) |
| `styles.py`, `.streamlit/config.toml` | Tema warna (teal gelap, krem hangat, aksen emas) |

## Landing page & reset akun
- Halaman pertama adalah landing page; isi tiap menu tampil setelah tombolnya diklik. Tombol **Login ke Sistem** membuka halaman login.
- Ubah profil, alamat, kontak, dan tahun copyright pada blok `PROFIL`, `KONTAK`, `TAHUN_COPYRIGHT` di `app.py`.
- Foto toko: file `foto_toko.jpg` (tampil di Home dan Profil Objek; ganti file ini untuk foto lain).
- Logo: simpan `logo.png` di folder yang sama dengan `app.py` (opsional).
- **Lupa username/password**: tombol di halaman login -> isi *kode pemulihan*, username baru, password baru.
  Kode bawaan `pemulihan-sembako`; ganti lewat variabel lingkungan `APP_RECOVERY` (atau `st.secrets`).

## Fitur hapus data
- **Kelola Data** → *Hapus Data Transaksi*: per nomor transaksi, per rentang tanggal, atau semua (ketik `HAPUS`).
- **Riwayat Analisis** → tombol *Hapus* per baris, dan *Hapus Semua Riwayat* (ketik `HAPUS`).
  Perbandingan & rekomendasi terkait ikut terhapus otomatis (`ON DELETE CASCADE`).
- Semua penghapusan memakai dialog konfirmasi.

## Catatan
- Nilai min support: 0,5%–20%; min confidence bawaan 50%; aturan valid bila lift > 1.
- Waktu eksekusi = lama fungsi `apriori()` / `fpgrowth()` berjalan.
- Hasil FP-Tree & CPB FP-Growth disimpan di kolom `data_frequent_itemset` (JSON), sehingga tetap bisa dilihat
  dari Riwayat Analisis walau data transaksi sudah dihapus.
- Untuk Streamlit Cloud: unggah seluruh folder ke GitHub; database SQLite di cloud bersifat sementara.
