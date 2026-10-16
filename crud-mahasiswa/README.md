# Aplikasi CRUD Data Mahasiswa

UTS Lab Pemrograman - Departemen Bisnis Digital, Universitas Diponegoro (Gasal 2026/2027).

Aplikasi web sederhana untuk mengelola data mahasiswa (Create, Read, Update, Delete)
dengan **Python + Flask** dan database **SQLite**.

## Fitur
- Tambah, lihat daftar, lihat detail, ubah, dan hapus mahasiswa
- Validasi: NIM, nama, program studi, angkatan, dan IPK wajib diisi; IPK harus 0.00-4.00
- NIM duplikat ditolak dengan pesan kesalahan (saat tambah maupun ubah)
- **Lama Studi (tahun)** = tahun sekarang - angkatan, dihitung otomatis oleh program
- Data tersimpan di file SQLite (`mahasiswa.db`) sehingga tetap ada setelah aplikasi dimatikan
- Pencarian berdasarkan NIM, nama, atau program studi

## Struktur
```
app.py            # backend Flask: route, validasi, akses database
templates/        # tampilan HTML (Jinja2)
static/style.css  # styling
test_app.py       # tes otomatis (pytest)
```

## Menjalankan
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Buka http://127.0.0.1:5000. File `mahasiswa.db` dibuat otomatis saat pertama dijalankan.

## Menjalankan tes
```bash
pip install pytest
python -m pytest
```

## Skema tabel `mahasiswa`
| Field | Tipe | Keterangan |
|---|---|---|
| id | INTEGER | primary key (otomatis) |
| nim | INTEGER | unique, wajib |
| nama | TEXT | wajib |
| program_studi | TEXT | wajib |
| angkatan | INTEGER | wajib |
| ipk | REAL | wajib, 0.00-4.00 |
