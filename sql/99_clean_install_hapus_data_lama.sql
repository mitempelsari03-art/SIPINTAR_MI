-- OPSIONAL: hanya jika ingin clean install dan rela menghapus data lama.
drop table if exists public.materi_tertunda cascade;
drop table if exists public.jurnal_guru cascade;
drop table if exists public.nilai_siswa cascade;
drop table if exists public.wa_outbox cascade;
drop table if exists public.tugas_siswa cascade;
drop table if exists public.pr_siswa cascade;
drop table if exists public.agenda_penilaian cascade;
drop table if exists public.dokumen_perangkat cascade;
drop table if exists public.kaldik_madrasah cascade;
drop table if exists public.rencana_harian cascade;
drop table if exists public.siswa_sipintar cascade;
drop table if exists public.guru_sipintar cascade;
drop table if exists public.app_users cascade;
