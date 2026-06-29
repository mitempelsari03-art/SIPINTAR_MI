# Template WA Jawa Krama

Template terdapat di fungsi `template_wa()` pada `app.py`.

Jenis notifikasi:
- `PR_DIBERIKAN`
- `TUGAS_DIBERIKAN`
- `NILAI_KELUAR`
- `BESOK_ULANGAN`
- `ULANG_TAHUN`

Semua pesan masuk ke tabel `wa_outbox` sebelum dikirim. Guru membuka menu **Komunikasi Orang Tua** untuk membuka link WhatsApp.
