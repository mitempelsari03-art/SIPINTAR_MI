# BLUEPRINT SIPINTAR_MI v10

## 1. Identitas Aplikasi

Nama aplikasi: SIPINTAR_MI  
Kepanjangan: Sistem Pintar Madrasah Ibtidaiyah  
Madrasah: MI Al Ma'arif Tempelsari  
Tahun Ajaran: 2025/2026  
Semester: 1  

---

## 2. Tujuan Aplikasi

SIPINTAR_MI dibuat untuk mengelola:

- Perangkat pembelajaran
- Jadwal mengajar harian
- Jurnal KBM
- PR dan tugas
- Penilaian
- Kokurikuler
- Absensi
- Iuran siswa
- Tabungan siswa
- Bendahara kelas
- Bendahara madrasah
- Laporan evaluasi
- Bahan akreditasi

---

## 3. Jenis User

### 3.1 GURU_MURNI

Fokus:
- Mengajar
- Absensi
- PR
- Tugas
- Nilai
- Kokurikuler
- Perangkat pembelajaran

Tidak memiliki akses Bendahara.

### 3.2 GURU_BENDAHARA

Memiliki semua akses Guru Murni, ditambah:
- Iuran siswa
- Tabungan siswa
- Bendahara kelas
- Rekap keuangan kelas

### 3.3 KEPSEK_KOMITE

Fokus monitoring:
- KBM berjalan
- Keuangan madrasah
- Iuran siswa
- Jurnal guru
- Laporan evaluasi
- Bahan akreditasi

Mayoritas akses bersifat lihat saja.

### 3.4 ADMIN_TU_BENDAHARA

Akses penuh:
- Upload/import data
- Download data
- Print data
- Data guru
- Data siswa
- Master data KBM
- Bendahara madrasah
- Pengaturan aplikasi
- Backup dan restore

---

## 4. Prinsip Tampilan

- Mobile-friendly
- Ubin berwarna
- Tombol besar
- Mudah dipakai guru lewat HP
- Sidebar tidak menjadi pusat utama
- Tabel dibuat sederhana dan bisa scroll
- Login hanya username dan password
- Latar login artistik bernuansa madrasah

---

## 5. Modul Inti

1. Login
2. Dashboard Role-Based
3. Mengajar Hari Ini
4. Perangkat Pembelajaran
5. Absensi
6. PR
7. Tugas
8. Penilaian
9. Kokurikuler
10. Iuran Siswa
11. Tabungan Siswa
12. Bendahara
13. Laporan
14. Admin Data
15. Pengaturan