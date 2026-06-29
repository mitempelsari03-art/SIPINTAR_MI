# ALUR MENU MENGAJAR HARI INI

## 1. Fungsi Utama

Menu "Mengajar Hari Ini" adalah pusat kerja harian guru.

Menu ini menampilkan otomatis:

- Jadwal mengajar hari ini
- Kelas
- Jam pelajaran
- Mata pelajaran
- Materi
- TP / tujuan pembelajaran
- Strategi pembelajaran
- Media
- Asesmen
- Catatan guru
- Tombol PR
- Tombol Tugas
- Tombol Kokurikuler
- Status pelaksanaan KBM

---

## 2. Sumber Data

Data berasal dari:

- tabel_jadwal_harian
- tabel_jadwal_induk
- tabel_kaldik
- tabel_mapel
- Bahan KBM AI.xlsx
- dokumen perangkat pembelajaran

---

## 3. Alur Guru

1. Guru login.
2. Guru klik ubin "Mengajar Hari Ini".
3. Aplikasi membaca jadwal berdasarkan:
   - tanggal hari ini,
   - nama guru,
   - kelas diampu,
   - jadwal harian.
4. Aplikasi menampilkan daftar KBM hari ini.
5. Guru memilih salah satu jadwal.
6. Guru membaca materi dan rencana pembelajaran.
7. Setelah pembelajaran, guru memilih status:
   - Terlaksana
   - Terlaksana Sebagian
   - Belum Terlaksana
8. Guru dapat mengisi:
   - catatan guru,
   - kendala,
   - tindak lanjut,
   - PR,
   - tugas,
   - kokurikuler temporer.
9. Guru klik Simpan.
10. Aplikasi membentuk jurnal KBM otomatis.

---

## 4. Status Pelaksanaan

### 4.1 Terlaksana

Jika guru memilih "Terlaksana":

- Data masuk ke jurnal KBM.
- Status jadwal berubah menjadi TERLAKSANA.
- Tidak perlu dijadwal ulang.

### 4.2 Terlaksana Sebagian

Jika guru memilih "Terlaksana Sebagian":

- Data masuk ke jurnal KBM.
- Guru wajib mengisi bagian yang belum selesai.
- Aplikasi membuat rencana tindak lanjut.
- Materi/TP yang belum selesai dijadwalkan ulang otomatis.

### 4.3 Belum Terlaksana

Jika guru memilih "Belum Terlaksana":

- Data masuk ke jurnal KBM sebagai belum terlaksana.
- Guru wajib mengisi alasan.
- Aplikasi mencari jadwal kosong atau jadwal mapel yang sama berikutnya.
- Materi/TP dijadwalkan ulang otomatis.
- Jadwal baru memiliki relasi ke jadwal lama.

---

## 5. Penjadwalan Ulang Otomatis

Jika KBM belum selesai, aplikasi melakukan:

1. Cari jadwal mapel yang sama berikutnya.
2. Jika ada, masukkan materi lanjutan ke jadwal tersebut.
3. Jika tidak ada, cari slot kosong.
4. Jika tetap tidak ada, masukkan ke daftar "Perlu Dijadwalkan Manual".
5. Admin/TU atau guru dapat menyesuaikan jadwal ulang.

Kolom penting:

- dijadwal_ulang_dari
- status_kbm
- tindak_lanjut
- alasan_tidak_terlaksana

---

## 6. Tombol PR

Tombol PR digunakan jika setelah KBM guru memberi pekerjaan rumah.

Data yang disimpan:

- tanggal
- guru
- kelas
- mapel
- isi PR
- batas pengumpulan
- catatan
- kirim WhatsApp atau tidak

PR otomatis masuk ke:

- jurnal KBM
- rekap PR
- notifikasi wali murid
- bahan evaluasi guru

---

## 7. Tombol Tugas

Tombol Tugas digunakan jika pembelajaran dilakukan dengan penugasan.

Data yang disimpan:

- tanggal
- guru
- kelas
- mapel
- jenis tugas
- isi tugas
- batas pengumpulan
- rubrik singkat
- catatan

Tugas otomatis masuk ke:

- jurnal KBM
- rekap tugas
- bahan penilaian
- dokumen evaluasi

---

## 8. Kokurikuler Temporer

Guru dapat mencatat kegiatan kokurikuler sewaktu-waktu.

Contoh:

- pembiasaan pagi
- kerja sama kelompok
- kepedulian
- cinta tanah air
- cinta lingkungan
- disiplin
- adab terhadap guru
- kegiatan kelas khusus

Data dikaitkan dengan:

- 8 Dimensi Profil Lulusan
- Panca Cinta
- kelas
- guru
- tanggal
- catatan kegiatan

---

## 9. Output Otomatis

Dari menu ini, aplikasi menghasilkan:

- Jurnal mengajar harian
- Rekap KBM mingguan
- Rekap KBM bulanan
- Rekap keterlaksanaan TP
- Rekap PR
- Rekap tugas
- Rekap kokurikuler
- Catatan tindak lanjut
- Dokumen evaluasi guru
- Bahan akreditasi

---

## 10. Prinsip Desain

Menu ini harus:

- sederhana
- mudah dipakai lewat HP
- tidak terlalu banyak form
- tombol besar
- data otomatis terisi
- guru cukup memilih dan mencatat seperlunya