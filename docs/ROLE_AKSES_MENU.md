# ROLE DAN HAK AKSES SIPINTAR_MI v10

## 1. Daftar Role

SIPINTAR_MI menggunakan 4 role utama:

1. GURU_MURNI
2. GURU_BENDAHARA
3. KEPSEK_KOMITE
4. ADMIN_TU_BENDAHARA

---

## 2. GURU_MURNI

Menu yang tampil:

- Mengajar Hari Ini
- Perangkat Pembelajaran
- Absensi Kelas
- PR
- Tugas
- Penilaian
- Kokurikuler
- Jurnal Mengajar
- WhatsApp Orang Tua

Tidak boleh melihat:

- Bendahara Kelas
- Bendahara Madrasah
- Import Data
- Backup Data
- Pengaturan User

---

## 3. GURU_BENDAHARA

Menu yang tampil:

- Semua menu GURU_MURNI
- Iuran Siswa
- Tabungan Siswa
- Bendahara Kelas
- Rekap Keuangan Kelas

---

## 4. KEPSEK_KOMITE

Menu yang tampil:

- Dashboard Monitoring
- Monitoring KBM
- Rekap Jurnal Guru
- Keuangan Madrasah
- Iuran Siswa
- Tabungan Siswa
- Laporan Akreditasi
- Perangkat Pembelajaran

Sifat akses:

- Mayoritas read-only
- Tidak input transaksi
- Tidak upload master data
- Tidak mengubah data guru/siswa

---

## 5. ADMIN_TU_BENDAHARA

Menu yang tampil:

- Dashboard Admin
- Import Master Data
- Upload Data Siswa
- Download Data
- Print Data
- Data Guru
- Data Siswa
- Data Mapel
- Data Jadwal
- Bendahara Madrasah
- Rekap Keuangan
- Backup dan Restore
- Pengaturan Aplikasi
- Log Aktivitas

Role ini merangkap TU dan Bendahara Madrasah.

---

## 6. Matriks Hak Akses

| Menu | Guru Murni | Guru Bendahara | Kepsek/Komite | Admin/TU Bendahara |
|---|---|---|---|---|
| Mengajar Hari Ini | Edit | Edit | Lihat | Lihat |
| Perangkat Pembelajaran | Lihat | Lihat | Lihat | Kelola |
| Absensi Kelas | Edit | Edit | Lihat | Kelola |
| PR | Edit | Edit | Lihat | Kelola |
| Tugas | Edit | Edit | Lihat | Kelola |
| Penilaian | Edit | Edit | Lihat | Kelola |
| Kokurikuler | Edit | Edit | Lihat | Kelola |
| Jurnal Mengajar | Edit | Edit | Lihat | Kelola |
| Iuran Siswa | Tidak | Edit | Lihat | Kelola |
| Tabungan Siswa | Tidak | Edit | Lihat | Kelola |
| Bendahara Kelas | Tidak | Edit | Lihat | Kelola |
| Bendahara Madrasah | Tidak | Tidak | Lihat | Kelola |
| Keuangan Madrasah | Tidak | Lihat Terbatas | Lihat | Kelola |
| Import Master Data | Tidak | Tidak | Tidak | Kelola |
| Upload Data Siswa | Tidak | Tidak | Tidak | Kelola |
| Backup Restore | Tidak | Tidak | Tidak | Kelola |
| Pengaturan User | Tidak | Tidak | Tidak | Kelola |