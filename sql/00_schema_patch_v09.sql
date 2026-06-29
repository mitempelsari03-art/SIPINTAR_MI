-- SIPINTAR-MI v0.9
-- Jalankan isi file ini di Supabase SQL Editor.
-- File ini aman untuk database lama: CREATE TABLE IF NOT EXISTS + ALTER ADD COLUMN.

create extension if not exists pgcrypto;

create table if not exists public.app_users (
  id text primary key default gen_random_uuid()::text,
  username text unique not null,
  password_hash text not null,
  nama text not null,
  role text not null default 'guru',
  guru_id text,
  is_active boolean default true,
  created_at timestamptz default now()
);

create table if not exists public.guru_sipintar (
  id text primary key,
  nama text,
  kelas text,
  jabatan text,
  role text default 'guru',
  username text,
  email_login text,
  password_hash text,
  no_wa text,
  is_active boolean default true
);

create table if not exists public.siswa_sipintar (
  id text primary key,
  nama text not null,
  kelas text not null,
  nomor_absen int,
  tanggal_lahir date,
  nama_ortu text,
  no_wa_ortu text
);

create table if not exists public.rencana_harian (
  id text primary key,
  tanggal date not null,
  hari text,
  guru_id text not null,
  guru_nama text,
  kelas text,
  mapel text,
  jam_mulai text,
  jam_selesai text,
  jp numeric,
  bab text,
  materi text,
  cp text,
  tp text,
  kktp text,
  media text,
  langkah_guru text,
  aktivitas_siswa text,
  alternatif text,
  lkpd_id text,
  soal_id text,
  tipe_kegiatan text default 'KBM',
  status_kbm text default 'belum_diisi'
);

create table if not exists public.kaldik_madrasah (
  tanggal date primary key,
  hari text,
  status_hari text,
  keterangan text,
  tipe_waktu text
);

create table if not exists public.dokumen_perangkat (
  id text primary key,
  guru_id text not null,
  guru_nama text,
  kelas text,
  semester int default 1,
  judul text,
  file_url text,
  file_path text,
  status text default 'Draft',
  created_at timestamptz default now()
);

create table if not exists public.agenda_penilaian (
  id text primary key,
  tanggal date not null,
  guru_id text not null,
  guru_nama text,
  kelas text,
  mapel text,
  bab text,
  unit_ke int,
  jenis text not null,
  bank_soal_id text,
  keterangan text,
  sumber text,
  status text default 'terjadwal'
);

create table if not exists public.pr_siswa (
  id text primary key,
  tanggal_diberikan date not null,
  tanggal_kumpul date not null,
  tanggal_periksa date not null,
  guru_id text not null,
  guru_nama text,
  kelas text,
  mapel text,
  bab text,
  sumber_pr text,
  halaman text,
  nomor_soal text,
  keterangan text,
  status text default 'terjadwal',
  created_at timestamptz default now()
);

create table if not exists public.tugas_siswa (
  id text primary key,
  tanggal_diberikan date not null,
  tanggal_kumpul date not null,
  guru_id text not null,
  guru_nama text,
  kelas text,
  mapel text,
  bab text,
  jenis_tugas text,
  keterangan text,
  status text default 'terjadwal',
  created_at timestamptz default now()
);

create table if not exists public.wa_outbox (
  id text primary key,
  tanggal date default current_date,
  jenis text,
  guru_id text,
  agenda_id text,
  siswa_id text,
  nama_siswa text,
  kelas text,
  nama_ortu text,
  no_wa_ortu text,
  pesan text,
  link_wa text,
  status text default 'siap_kirim',
  created_at timestamptz default now(),
  sent_at timestamptz
);

create table if not exists public.nilai_siswa (
  id uuid primary key default gen_random_uuid(),
  agenda_id text not null,
  siswa_id text not null,
  guru_id text,
  kelas text,
  mapel text,
  jenis text,
  nilai numeric default 0,
  nilai_uh numeric default 0,
  nilai_tugas numeric default 0,
  nilai_pr numeric default 0,
  nilai_asas numeric default 0,
  nilai_remedial numeric,
  nilai_akhir numeric default 0,
  rata_harian numeric default 0,
  updated_at timestamptz default now(),
  unique(agenda_id, siswa_id)
);

create table if not exists public.jurnal_guru (
  id uuid primary key default gen_random_uuid(),
  rencana_id text unique,
  tanggal date,
  guru_id text,
  kelas text,
  mapel text,
  bab text,
  materi text,
  status_ketuntasan text,
  persentase_terlaksana int,
  catatan_guru text,
  jurnal_otomatis text,
  created_at timestamptz default now()
);

create table if not exists public.materi_tertunda (
  id uuid primary key default gen_random_uuid(),
  rencana_asal_id text,
  guru_id text,
  kelas text,
  mapel text,
  bab text,
  materi text,
  persentase_sisa int,
  tanggal_asal date,
  tanggal_pengganti date,
  mode_penjadwalan text,
  status text default 'tertunda',
  created_at timestamptz default now()
);

-- Patch kolom untuk database lama
alter table if exists public.guru_sipintar add column if not exists email_login text;
alter table if exists public.guru_sipintar add column if not exists username text;
alter table if exists public.guru_sipintar add column if not exists password_hash text;
alter table if exists public.guru_sipintar add column if not exists role text default 'guru';
alter table if exists public.guru_sipintar add column if not exists no_wa text;
alter table if exists public.guru_sipintar add column if not exists is_active boolean default true;

alter table if exists public.siswa_sipintar add column if not exists tanggal_lahir date;
alter table if exists public.siswa_sipintar add column if not exists nama_ortu text;
alter table if exists public.siswa_sipintar add column if not exists no_wa_ortu text;

alter table if exists public.nilai_siswa add column if not exists nilai numeric default 0;
alter table if exists public.nilai_siswa add column if not exists nilai_asas numeric default 0;
alter table if exists public.nilai_siswa add column if not exists nilai_akhir numeric default 0;

select pg_notify('pgrst', 'reload schema');
