import hashlib
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from supabase import create_client

APP_TITLE = "SIPINTAR-MI v1.0"

@st.cache_resource
def db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_ROLE_KEY"])

def hp(p):
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def login(username, password):
    rows = db().table("app_users").select("*").eq("username", username.strip().lower()).eq("is_active", True).execute().data or []
    if rows and rows[0].get("password_hash") == hp(password):
        return rows[0]
    return None

def iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else d

def norm_wa(no):
    if not no:
        return ""
    s = str(no).replace(" ", "").replace("-", "").replace("+", "").strip()
    if s.startswith("0"):
        return "62" + s[1:]
    if s.startswith("8"):
        return "62" + s
    return s

def wa_link(no, pesan):
    no = norm_wa(no)
    return f"https://wa.me/{no}?text={urllib.parse.quote(pesan)}" if no else ""

def q(table):
    return db().table(table)



# =====================================================
# KONFIGURASI IMPORT DATA v1.0
# =====================================================
TABLE_CONFIG = {
    "app_users": {
        "label": "Akun Pengguna",
        "required": ["id", "username", "password_hash", "nama", "role"],
        "date_cols": [],
        "int_cols": [],
        "numeric_cols": [],
        "bool_cols": ["is_active"],
        "default_on_conflict": "id",
    },
    "guru_sipintar": {
        "label": "Data Guru",
        "required": ["id", "nama"],
        "date_cols": [],
        "int_cols": [],
        "numeric_cols": [],
        "bool_cols": ["is_active"],
        "default_on_conflict": "id",
    },
    "siswa_sipintar": {
        "label": "Data Siswa",
        "required": ["id", "nama", "kelas"],
        "date_cols": ["tanggal_lahir"],
        "int_cols": ["nomor_absen"],
        "numeric_cols": [],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
    "rencana_harian": {
        "label": "Rencana Harian / Jadwal Mengajar",
        "required": ["id", "tanggal", "guru_id"],
        "date_cols": ["tanggal"],
        "int_cols": [],
        "numeric_cols": ["jp"],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
    "agenda_penilaian": {
        "label": "Agenda Penilaian",
        "required": ["id", "tanggal", "guru_id", "jenis"],
        "date_cols": ["tanggal"],
        "int_cols": ["unit_ke"],
        "numeric_cols": [],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
    "pr_siswa": {
        "label": "PR Siswa",
        "required": ["id", "tanggal_diberikan", "tanggal_kumpul", "tanggal_periksa", "guru_id"],
        "date_cols": ["tanggal_diberikan", "tanggal_kumpul", "tanggal_periksa"],
        "int_cols": [],
        "numeric_cols": [],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
    "tugas_siswa": {
        "label": "Tugas Siswa",
        "required": ["id", "tanggal_diberikan", "tanggal_kumpul", "guru_id"],
        "date_cols": ["tanggal_diberikan", "tanggal_kumpul"],
        "int_cols": [],
        "numeric_cols": [],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
    "dokumen_perangkat": {
        "label": "Dokumen Perangkat (Opsional)",
        "required": ["id", "guru_id"],
        "date_cols": [],
        "int_cols": ["semester"],
        "numeric_cols": [],
        "bool_cols": [],
        "default_on_conflict": "id",
    },
}

IMPORT_UTAMA = ["guru_sipintar", "siswa_sipintar", "rencana_harian", "agenda_penilaian", "pr_siswa", "tugas_siswa"]


def _bersihkan_nama_kolom(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def baca_file_import(file):
    nama = file.name.lower()
    if nama.endswith(".csv"):
        try:
            return pd.read_csv(file, dtype=str)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, dtype=str, encoding="latin1")
    if nama.endswith((".xlsx", ".xls")):
        return pd.read_excel(file, dtype=str)
    raise ValueError("Format file belum didukung. Gunakan CSV atau Excel.")


def normalisasi_dataframe(df, table):
    cfg = TABLE_CONFIG[table]
    df = _bersihkan_nama_kolom(df)
    df = df.dropna(how="all")
    df = df.where(pd.notnull(df), None)

    missing = [c for c in cfg["required"] if c not in df.columns]
    if missing:
        return None, f"Kolom wajib belum ada: {', '.join(missing)}"

    for col in cfg["date_cols"]:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            df[col] = parsed.dt.date.astype("string")
            df[col] = df[col].replace({"NaT": None, "<NA>": None})

    for col in cfg["int_cols"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64").astype("object")
            df[col] = df[col].where(pd.notnull(df[col]), None)

    for col in cfg["numeric_cols"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].where(pd.notnull(df[col]), None)

    for col in cfg["bool_cols"]:
        if col in df.columns:
            df[col] = df[col].map(lambda x: True if str(x).strip().lower() in ["true", "1", "ya", "aktif", "yes"] else False if str(x).strip().lower() in ["false", "0", "tidak", "nonaktif", "no"] else None)

    # Hilangkan baris tanpa id agar tidak gagal saat upsert.
    if "id" in df.columns:
        df = df[df["id"].notna() & (df["id"].astype(str).str.strip() != "")]

    records = df.to_dict("records")
    clean_records = []
    for r in records:
        clean_records.append({k: (None if pd.isna(v) else v) for k, v in r.items()})
    return clean_records, None


def import_records(table, records, chunk_size=500):
    total = 0
    conflict = TABLE_CONFIG[table].get("default_on_conflict", "id")
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        q(table).upsert(chunk, on_conflict=conflict).execute()
        total += len(chunk)
    return total


def buat_template_csv(table):
    cfg = TABLE_CONFIG[table]
    cols = cfg["required"] + [c for c in (cfg["date_cols"] + cfg["int_cols"] + cfg["numeric_cols"] + cfg["bool_cols"]) if c not in cfg["required"]]
    contoh = {c: "" for c in cols}
    if table == "siswa_sipintar":
        contoh.update({"id":"SIS-001", "nama":"Ahmad", "kelas":"1A", "nomor_absen":"1", "tanggal_lahir":"2018-06-28", "nama_ortu":"Bapak/Ibu Ahmad", "no_wa_ortu":"628123456789"})
    elif table == "guru_sipintar":
        contoh.update({"id":"GURU-001", "nama":"Guru Kelas 1", "kelas":"1A", "jabatan":"Guru Kelas", "role":"guru", "username":"guru1", "is_active":"true"})
    elif table == "rencana_harian":
        contoh.update({"id":"RH-001", "tanggal":"2026-07-13", "guru_id":"GURU-001", "kelas":"1A", "mapel":"Bahasa Indonesia", "bab":"Bab 1", "materi":"Mengenal huruf"})
    return pd.DataFrame([contoh]).to_csv(index=False).encode("utf-8")


def kelas_guru(guru_id):
    rows = q("rencana_harian").select("kelas").eq("guru_id", guru_id).execute().data or []
    return sorted({r.get("kelas") for r in rows if r.get("kelas")})

def mapel_guru(guru_id, kelas=None):
    query = q("rencana_harian").select("mapel").eq("guru_id", guru_id)
    if kelas:
        query = query.eq("kelas", kelas)
    rows = query.execute().data or []
    return sorted({r.get("mapel") for r in rows if r.get("mapel")})

def bab_guru(guru_id, kelas, mapel):
    rows = q("rencana_harian").select("bab").eq("guru_id", guru_id).eq("kelas", kelas).eq("mapel", mapel).execute().data or []
    return sorted({r.get("bab") for r in rows if r.get("bab")})

def siswa_kelas(kelas):
    return q("siswa_sipintar").select("*").eq("kelas", kelas).order("nomor_absen").order("nama").execute().data or []

def tgl_lahir_sama(tanggal_lahir, tanggal):
    if not tanggal_lahir:
        return False
    try:
        t = datetime.fromisoformat(str(tanggal_lahir)).date()
        return t.month == tanggal.month and t.day == tanggal.day
    except Exception:
        return False

# =====================================================
# TEMPLATE WA JAWA KRAMA
# =====================================================
def template_wa(jenis, c):
    nama = c.get("nama_siswa", "Ananda")
    mapel = c.get("mapel", "-")
    materi = c.get("materi") or c.get("bab") or "-"
    if jenis == "PR_DIBERIKAN":
        return f"""Assalamu’alaikum warahmatullahi wabarakatuh.

Bapak/Ibu Wali saking Ananda {nama}, nyuwun pirsa bilih wonten PR mata pelajaran {mapel}, babagan {materi}.

PR dipunparingaken dinten {c.get('tanggal_diberikan','-')}, dipunkempalaken dinten {c.get('tanggal_kumpul','-')}, saha badhe dipunpriksa dinten {c.get('tanggal_periksa','-')}.

Mugi Bapak/Ibu kersa ndampingi Ananda sinau wonten griya kanthi sae.

Maturnuwun.
MI Al Ma’arif Tempelsari"""
    if jenis == "TUGAS_DIBERIKAN":
        return f"""Assalamu’alaikum warahmatullahi wabarakatuh.

Bapak/Ibu Wali saking Ananda {nama}, nyuwun pirsa bilih wonten tugas mata pelajaran {mapel}, babagan {materi}.

Tugas dipunparingaken dinten {c.get('tanggal_diberikan','-')} lan dipunkempalaken dinten {c.get('tanggal_kumpul','-')}.

Mugi Bapak/Ibu kersa paring panyengkuyung dhateng Ananda.

Maturnuwun.
MI Al Ma’arif Tempelsari"""
    if jenis == "NILAI_KELUAR":
        return f"""Assalamu’alaikum warahmatullahi wabarakatuh.

Bapak/Ibu Wali saking Ananda {nama}, nyuwun pirsa bilih asil biji {c.get('jenis_nilai','-')} mata pelajaran {mapel} inggih punika {c.get('nilai','-')}.

Mugi dados bahan pangertosan lan panyengkuyung supados Ananda langkung sregep sinau wonten griya.

Maturnuwun.
MI Al Ma’arif Tempelsari"""
    if jenis == "BESOK_ULANGAN":
        return f"""Assalamu’alaikum warahmatullahi wabarakatuh.

Bapak/Ibu Wali saking Ananda {nama}, nyuwun pirsa bilih benjing tanggal {c.get('tanggal_ulangan','-')} badhe wonten ulangan/asesmen {mapel}, babagan {materi}.

Mugi Bapak/Ibu kersa ndampingi Ananda sinau lan nyiapaken pirantos sekolah kanthi sae.

Maturnuwun.
MI Al Ma’arif Tempelsari"""
    if jenis == "ULANG_TAHUN":
        return f"""Assalamu’alaikum warahmatullahi wabarakatuh.

Kagem Ananda {nama}, sugeng ambal warsa.

Mugi tansah pinaringan sehat, tambah sregep sinau, dados putra/putri ingkang shalih/shalihah, bekti dhumateng tiyang sepuh, saha migunani tumrap agama, kulawarga, lan masyarakat.

Maturnuwun.
MI Al Ma’arif Tempelsari"""
    return ""

def buat_wa(jenis, siswa, ctx, guru_id=None, agenda_id=None):
    pesan = template_wa(jenis, {**ctx, "nama_siswa": siswa.get("nama")})
    data = {
        "id": f"{jenis}-{agenda_id or ctx.get('id_ref','')}-{siswa.get('id')}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "tanggal": date.today().isoformat(),
        "jenis": jenis,
        "guru_id": guru_id,
        "agenda_id": agenda_id,
        "siswa_id": siswa.get("id"),
        "nama_siswa": siswa.get("nama"),
        "kelas": siswa.get("kelas") or ctx.get("kelas"),
        "nama_ortu": siswa.get("nama_ortu"),
        "no_wa_ortu": siswa.get("no_wa_ortu"),
        "pesan": pesan,
        "link_wa": wa_link(siswa.get("no_wa_ortu"), pesan),
        "status": "siap_kirim",
        "created_at": datetime.now().isoformat(),
    }
    q("wa_outbox").upsert(data, on_conflict="id").execute()
    return data

# =====================================================
# DASHBOARD
# =====================================================
def halaman_dashboard(user):
    st.header("🏠 Dashboard Guru")
    tanggal = st.date_input("Tanggal aktif", value=date.today())
    gid = user.get("guru_id")
    besok = tanggal + timedelta(days=1)

    st.subheader("🔔 Pengingat")
    pr_periksa = q("pr_siswa").select("*").eq("guru_id", gid).eq("tanggal_periksa", iso(tanggal)).neq("status", "diperiksa").execute().data or []
    pr_kumpul = q("pr_siswa").select("*").eq("guru_id", gid).eq("tanggal_kumpul", iso(tanggal)).neq("status", "selesai").execute().data or []
    uh_besok = q("agenda_penilaian").select("*").eq("guru_id", gid).eq("tanggal", iso(besok)).in_("jenis", ["UH", "ASLM", "ASAS"]).execute().data or []

    kelas = kelas_guru(gid)
    siswa = q("siswa_sipintar").select("*").execute().data or []
    ultah = [s for s in siswa if s.get("kelas") in kelas and tgl_lahir_sama(s.get("tanggal_lahir"), tanggal)]

    if not pr_periksa and not pr_kumpul and not uh_besok and not ultah:
        st.success("Tidak ada pengingat khusus hari ini.")
    for p in pr_kumpul:
        st.info(f"📥 PR dikumpulkan hari ini: {p.get('kelas')} | {p.get('mapel')} | {p.get('bab')}")
    for p in pr_periksa:
        st.warning(f"📚 Hari ini waktunya memeriksa PR: {p.get('kelas')} | {p.get('mapel')} | {p.get('bab')}")
    for u in uh_besok:
        st.error(f"🧾 Besok ada {u.get('jenis')}: {u.get('kelas')} | {u.get('mapel')} | {u.get('bab')}")
    for s in ultah:
        st.success(f"🎂 Ulang tahun hari ini: {s.get('nama')} ({s.get('kelas')})")

    c1, c2 = st.columns(2)
    with c1:
        if uh_besok and st.button("📲 Buat WA Pengingat Besok Ulangan"):
            total = 0
            for ag in uh_besok:
                for s in siswa_kelas(ag.get("kelas")):
                    buat_wa("BESOK_ULANGAN", s, {"kelas": ag.get("kelas"), "mapel": ag.get("mapel"), "bab": ag.get("bab"), "materi": ag.get("bab"), "tanggal_ulangan": ag.get("tanggal"), "id_ref": ag.get("id")}, gid, ag.get("id"))
                    total += 1
            st.success(f"{total} pesan pengingat ulangan masuk antrean WA.")
    with c2:
        if ultah and st.button("🎂 Buat WA Ucapan Ulang Tahun"):
            for s in ultah:
                buat_wa("ULANG_TAHUN", s, {"id_ref": f"ultah-{tanggal}"}, gid)
            st.success(f"{len(ultah)} ucapan ulang tahun masuk antrean WA.")

# =====================================================
# HARI INI
# =====================================================
def halaman_hari_ini(user):
    st.header("📅 Hari Ini Saya Mengajar")
    gid = user.get("guru_id")
    tanggal = st.date_input("Tanggal mengajar", value=date.today(), key="tgl_mengajar")
    if st.button("📘 Buka Perangkat Pembelajaran Semester 1"):
        st.session_state["menu"] = "Perangkat Pembelajaran"
        st.rerun()
    rows = q("rencana_harian").select("*").eq("guru_id", gid).eq("tanggal", iso(tanggal)).order("jam_mulai").execute().data or []
    if not rows:
        st.info("Tidak ada jadwal mengajar pada tanggal ini.")
        return
    for r in rows:
        st.divider()
        st.subheader(f"{r.get('jam_mulai','')}–{r.get('jam_selesai','')} | {r.get('kelas','')} | {r.get('mapel','')}")
        if r.get("tipe_kegiatan") == "PJOK_DI_GURU_KELAS":
            st.info("Siswa mengikuti pelajaran PJOK bersama guru PJOK.")
            continue
        st.markdown("**CP**"); st.write(r.get("cp", "-"))
        st.markdown("**TP**"); st.write(r.get("tp", "-"))
        st.markdown("**KKTP**"); st.write(r.get("kktp", "-"))
        st.markdown("**Materi/BAB**"); st.write(f"{r.get('bab','-')} — {r.get('materi','-')}")
        status = st.radio("Status", ["Tuntas", "Sebagian Tuntas", "Belum Terlaksana"], horizontal=True, key=f"st_{r['id']}")
        catatan = st.selectbox("Catatan cepat", ["Tidak ada catatan khusus", "Siswa sudah memahami materi", "Sebagian siswa perlu penguatan", "Waktu tidak cukup", "Kelas kurang kondusif", "Ada kegiatan madrasah", "Perlu remedial", "Perlu pengayaan"], key=f"ct_{r['id']}")
        persen = 100 if status == "Tuntas" else 0
        if status == "Sebagian Tuntas":
            persen = st.slider("Perkiraan terlaksana", 10, 90, 60, 10, key=f"ps_{r['id']}")
        if st.button("💾 Simpan Jurnal Otomatis", key=f"sv_{r['id']}"):
            status_db = {"Tuntas":"tuntas", "Sebagian Tuntas":"sebagian", "Belum Terlaksana":"belum"}[status]
            q("jurnal_guru").upsert({"rencana_id": r["id"], "tanggal": r["tanggal"], "guru_id": gid, "kelas": r.get("kelas"), "mapel": r.get("mapel"), "bab": r.get("bab"), "materi": r.get("materi"), "status_ketuntasan": status_db, "persentase_terlaksana": persen, "catatan_guru": catatan, "jurnal_otomatis": f"Pembelajaran {r.get('mapel')} kelas {r.get('kelas')} materi {r.get('materi')} berstatus {status_db}. Catatan: {catatan}.", "created_at": datetime.now().isoformat()}, on_conflict="rencana_id").execute()
            q("rencana_harian").update({"status_kbm": status_db}).eq("id", r["id"]).execute()
            st.success("Jurnal tersimpan.")
            st.rerun()

# =====================================================
# PR DAN TUGAS
# =====================================================
def halaman_pr(user):
    st.header("📚 PR")
    gid = user.get("guru_id")
    tab1, tab2 = st.tabs(["Buat PR", "Daftar PR"])
    with tab1:
        kelas = st.selectbox("Kelas", kelas_guru(gid) or ["-"])
        mapel = st.selectbox("Mapel", mapel_guru(gid, kelas) or ["-"])
        bab = st.selectbox("BAB/Materi", bab_guru(gid, kelas, mapel) or ["-"])
        a,b,c = st.columns(3)
        with a: t_beri = st.date_input("Tanggal PR diberikan", value=date.today())
        with b: t_kumpul = st.date_input("Tanggal PR dikumpulkan", value=date.today()+timedelta(days=2))
        with c: t_periksa = st.date_input("Tanggal PR diperiksa", value=date.today()+timedelta(days=3))
        sumber = st.selectbox("Sumber PR", ["LKS", "Buku Paket", "Buatan Guru", "Pengamatan Lingkungan", "Proyek Sederhana", "Lainnya"])
        halaman = st.text_input("Halaman")
        nomor = st.text_input("Nomor soal")
        ket = st.text_area("Keterangan singkat")
        if st.button("💾 Simpan PR & Siapkan WA"):
            pr_id = f"PR-{gid}-{kelas}-{mapel}-{datetime.now().strftime('%Y%m%d%H%M%S')}".replace(" ", "_")
            data = {"id": pr_id, "tanggal_diberikan": iso(t_beri), "tanggal_kumpul": iso(t_kumpul), "tanggal_periksa": iso(t_periksa), "guru_id": gid, "guru_nama": user.get("nama"), "kelas": kelas, "mapel": mapel, "bab": bab, "sumber_pr": sumber, "halaman": halaman, "nomor_soal": nomor, "keterangan": ket, "status": "terjadwal", "created_at": datetime.now().isoformat()}
            q("pr_siswa").upsert(data, on_conflict="id").execute()
            q("agenda_penilaian").upsert({"id": pr_id, "tanggal": iso(t_kumpul), "guru_id": gid, "guru_nama": user.get("nama"), "kelas": kelas, "mapel": mapel, "bab": bab, "jenis": "PR", "keterangan": f"{sumber} hlm {halaman} nomor {nomor}. Diperiksa {iso(t_periksa)}", "sumber": "PR Guru", "status": "terjadwal"}, on_conflict="id").execute()
            total=0
            for s in siswa_kelas(kelas):
                buat_wa("PR_DIBERIKAN", s, {"id_ref": pr_id, "kelas": kelas, "mapel": mapel, "bab": bab, "materi": bab, "tanggal_diberikan": t_beri.strftime('%d-%m-%Y'), "tanggal_kumpul": t_kumpul.strftime('%d-%m-%Y'), "tanggal_periksa": t_periksa.strftime('%d-%m-%Y')}, gid, pr_id)
                total += 1
            st.success(f"PR tersimpan. {total} notifikasi WA masuk antrean.")
    with tab2:
        rows = q("pr_siswa").select("*").eq("guru_id", gid).order("tanggal_diberikan", desc=True).execute().data or []
        if rows:
            st.dataframe(pd.DataFrame(rows)[["tanggal_diberikan","tanggal_kumpul","tanggal_periksa","kelas","mapel","bab","sumber_pr","halaman","nomor_soal","status"]], use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada PR.")

def halaman_tugas(user):
    st.header("📝 Tugas")
    gid = user.get("guru_id")
    tab1, tab2 = st.tabs(["Buat Tugas", "Daftar Tugas"])
    with tab1:
        kelas = st.selectbox("Kelas", kelas_guru(gid) or ["-"], key="tgs_kelas")
        mapel = st.selectbox("Mapel", mapel_guru(gid, kelas) or ["-"], key="tgs_mapel")
        bab = st.selectbox("BAB/Materi", bab_guru(gid, kelas, mapel) or ["-"], key="tgs_bab")
        jenis = st.selectbox("Jenis tugas", ["Individu", "Kelompok", "Proyek sederhana", "Praktik", "Karya"])
        a,b = st.columns(2)
        with a: t_beri = st.date_input("Tanggal tugas diberikan", value=date.today())
        with b: t_kumpul = st.date_input("Tanggal tugas dikumpulkan", value=date.today()+timedelta(days=5))
        ket = st.text_area("Keterangan tugas")
        kirim_wa = st.checkbox("Siapkan WA ke orang tua", value=False)
        if st.button("💾 Simpan Tugas"):
            tid = f"TGS-{gid}-{kelas}-{mapel}-{datetime.now().strftime('%Y%m%d%H%M%S')}".replace(" ", "_")
            q("tugas_siswa").upsert({"id": tid, "tanggal_diberikan": iso(t_beri), "tanggal_kumpul": iso(t_kumpul), "guru_id": gid, "guru_nama": user.get("nama"), "kelas": kelas, "mapel": mapel, "bab": bab, "jenis_tugas": jenis, "keterangan": ket, "status": "terjadwal", "created_at": datetime.now().isoformat()}, on_conflict="id").execute()
            q("agenda_penilaian").upsert({"id": tid, "tanggal": iso(t_kumpul), "guru_id": gid, "guru_nama": user.get("nama"), "kelas": kelas, "mapel": mapel, "bab": bab, "jenis": "Tugas", "keterangan": ket, "sumber": "Tugas Guru", "status": "terjadwal"}, on_conflict="id").execute()
            total=0
            if kirim_wa:
                for s in siswa_kelas(kelas):
                    buat_wa("TUGAS_DIBERIKAN", s, {"id_ref": tid, "kelas": kelas, "mapel": mapel, "bab": bab, "materi": bab, "tanggal_diberikan": t_beri.strftime('%d-%m-%Y'), "tanggal_kumpul": t_kumpul.strftime('%d-%m-%Y')}, gid, tid)
                    total += 1
            st.success(f"Tugas tersimpan. {total} notifikasi WA disiapkan.")
    with tab2:
        rows = q("tugas_siswa").select("*").eq("guru_id", gid).order("tanggal_diberikan", desc=True).execute().data or []
        if rows:
            st.dataframe(pd.DataFrame(rows)[["tanggal_diberikan","tanggal_kumpul","kelas","mapel","bab","jenis_tugas","status"]], use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada tugas.")

# =====================================================
# UH, NILAI, WA, PERANGKAT
# =====================================================
def halaman_uh(user):
    st.header("🧾 Jadwal UH/ASLM/ASAS")
    rows = q("agenda_penilaian").select("*").eq("guru_id", user.get("guru_id")).in_("jenis", ["UH","ASLM","ASAS"]).order("tanggal").execute().data or []
    if rows:
        st.dataframe(pd.DataFrame(rows)[["tanggal","kelas","mapel","bab","jenis","bank_soal_id","status"]], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada jadwal ulangan.")

def halaman_nilai(user):
    st.header("📊 Input Nilai Ringkas")
    gid = user.get("guru_id")
    ags = q("agenda_penilaian").select("*").eq("guru_id", gid).in_("jenis", ["UH","ASLM","PR","Tugas","ASAS"]).order("tanggal", desc=True).execute().data or []
    if not ags:
        st.info("Belum ada agenda penilaian.")
        return
    ids=[a["id"] for a in ags]
    agid = st.selectbox("Agenda", ids, format_func=lambda x: next(f"{a['tanggal']} | {a['jenis']} | {a['kelas']} | {a['mapel']} | {a.get('bab','')}" for a in ags if a["id"]==x))
    ag = next(a for a in ags if a["id"] == agid)
    siswa = siswa_kelas(ag.get("kelas"))
    old = q("nilai_siswa").select("*").eq("agenda_id", agid).execute().data or []
    oldmap = {o["siswa_id"]: o for o in old}
    df = pd.DataFrame([{"siswa_id":s["id"], "Nama Siswa":s["nama"], "Nilai":oldmap.get(s["id"],{}).get("nilai",0), "Remedial":oldmap.get(s["id"],{}).get("nilai_remedial",None)} for s in siswa])
    edited = st.data_editor(df.drop(columns=["siswa_id"]), use_container_width=True, hide_index=True)
    kirim = st.checkbox("Siapkan notifikasi WA nilai", value=True)
    if st.button("💾 Simpan Nilai"):
        payload=[]; total=0
        for i,r in edited.iterrows():
            s = siswa[i]
            nilai = float(r.get("Nilai") or 0)
            rem = r.get("Remedial")
            remv = None if pd.isna(rem) or rem == "" else float(rem)
            akhir = max(nilai, remv) if remv is not None else nilai
            payload.append({"agenda_id":agid,"siswa_id":s["id"],"guru_id":gid,"kelas":ag.get("kelas"),"mapel":ag.get("mapel"),"jenis":ag.get("jenis"),"nilai":nilai,"nilai_remedial":remv,"nilai_akhir":akhir,"updated_at":datetime.now().isoformat()})
            if kirim:
                buat_wa("NILAI_KELUAR", s, {"id_ref":agid,"kelas":ag.get("kelas"),"mapel":ag.get("mapel"),"bab":ag.get("bab"),"jenis_nilai":ag.get("jenis"),"nilai":akhir}, gid, agid)
                total += 1
        q("nilai_siswa").upsert(payload, on_conflict="agenda_id,siswa_id").execute()
        st.success(f"Nilai tersimpan. {total} notifikasi WA masuk antrean.")

def halaman_wa(user):
    st.header("📲 Komunikasi Orang Tua / WA")
    st.caption("Mode aman: aplikasi menyiapkan pesan Jawa krama dan link wa.me. Otomatis penuh perlu WhatsApp Business API resmi.")
    rows = q("wa_outbox").select("*").eq("guru_id", user.get("guru_id")).order("created_at", desc=True).limit(200).execute().data or []
    if not rows:
        st.info("Belum ada antrean WA.")
        return
    filt = st.selectbox("Filter", ["semua", "siap_kirim", "terkirim", "dibatalkan"])
    if filt != "semua": rows = [r for r in rows if r.get("status") == filt]
    for r in rows:
        with st.expander(f"{r.get('jenis')} | {r.get('kelas')} | {r.get('nama_siswa')} | {r.get('status')}"):
            st.text_area("Pesan", r.get("pesan",""), height=180, key=f"msg_{r['id']}")
            if r.get("link_wa"):
                st.link_button("📲 Buka WhatsApp", r.get("link_wa"))
            if st.button("Tandai terkirim", key=f"sent_{r['id']}"):
                q("wa_outbox").update({"status":"terkirim", "sent_at":datetime.now().isoformat()}).eq("id", r["id"]).execute(); st.rerun()

def halaman_perangkat(user):
    st.header("📘 Perangkat Pembelajaran")
    rows = q("dokumen_perangkat").select("*").eq("guru_id", user.get("guru_id")).eq("semester", 1).execute().data or []
    if not rows:
        st.warning("Dokumen perangkat belum disambungkan."); return
    d = rows[0]
    st.subheader(d.get("judul", "Perangkat Pembelajaran"))
    if d.get("file_url"):
        st.link_button("📖 Buka Dokumen", d.get("file_url"))
    elif d.get("file_path") and Path(d.get("file_path")).exists():
        with open(d.get("file_path"), "rb") as f:
            st.download_button("📥 Unduh/Buka Dokumen", f, file_name=Path(d.get("file_path")).name)
    else:
        st.info("Link/file dokumen belum tersedia.")

def halaman_admin():
    st.header("⚙️ Admin Data")
    st.info("Versi 1.0: import data dibuat lebih aman. Data perangkat pembelajaran tidak ikut muncul/diimport kecuali dipilih manual.")

    mode = st.radio(
        "Pilih mode import",
        ["Data Utama SIPINTAR", "Semua Tabel", "Dokumen Perangkat Saja"],
        horizontal=True,
        help="Data Utama tidak memasukkan tabel dokumen_perangkat agar upload data harian tidak bercampur dokumen perangkat."
    )

    if mode == "Data Utama SIPINTAR":
        tables = IMPORT_UTAMA
    elif mode == "Dokumen Perangkat Saja":
        tables = ["dokumen_perangkat"]
    else:
        tables = list(TABLE_CONFIG.keys())

    st.warning("Pastikan SQL schema v1.0 sudah dijalankan di Supabase sebelum import.")
    st.caption("Format didukung: CSV, XLSX, XLS. Nama kolom boleh huruf besar/kecil dan spasi akan otomatis dibaca sebagai underscore.")

    for tb in tables:
        cfg = TABLE_CONFIG[tb]
        with st.expander(f"Import {cfg['label']} — tabel `{tb}`", expanded=(tb == tables[0])):
            st.write("Kolom wajib:", ", ".join(cfg["required"]))
            st.download_button(
                "📥 Unduh template CSV",
                data=buat_template_csv(tb),
                file_name=f"template_{tb}.csv",
                mime="text/csv",
                key=f"tpl_{tb}"
            )
            f = st.file_uploader(f"Upload CSV/Excel untuk {tb}", type=["csv", "xlsx", "xls"], key=f"up_{tb}")
            if f:
                try:
                    df_raw = baca_file_import(f)
                    df_preview = _bersihkan_nama_kolom(df_raw).head(10)
                    st.caption("Pratinjau 10 baris pertama:")
                    st.dataframe(df_preview, use_container_width=True, hide_index=True)
                    records, err = normalisasi_dataframe(df_raw, tb)
                    if err:
                        st.error(err)
                        continue
                    st.success(f"File terbaca: {len(records)} baris siap import.")
                    if st.button(f"✅ Import ke tabel {tb}", key=f"btn_{tb}"):
                        if not records:
                            st.warning("Tidak ada baris valid untuk diimport.")
                        else:
                            total = import_records(tb, records)
                            st.success(f"{total} baris berhasil diimport ke `{tb}`.")
                except Exception as e:
                    st.error("Import gagal. Periksa format file, nama kolom, dan koneksi Supabase.")
                    st.exception(e)

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title("SIPINTAR-MI")
    if "user" not in st.session_state:
        st.subheader("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            user = login(u,p)
            if user:
                st.session_state["user"] = user; st.rerun()
            else:
                st.error("Username/password salah.")
        return
    user = st.session_state["user"]
    menus = ["Dashboard", "Hari Ini Saya Mengajar", "Perangkat Pembelajaran", "PR", "Tugas", "Jadwal UH/ASLM", "Input Nilai", "Komunikasi Orang Tua"]
    if user.get("role") == "admin": menus.append("Admin Data")
    with st.sidebar:
        st.write(f"👋 {user.get('nama')}")
        m = st.radio("Menu", menus, index=menus.index(st.session_state.get("menu", menus[0])) if st.session_state.get("menu", menus[0]) in menus else 0)
        st.session_state["menu"] = m
        if st.button("Logout"):
            st.session_state.clear(); st.rerun()
    if m == "Dashboard": halaman_dashboard(user)
    elif m == "Hari Ini Saya Mengajar": halaman_hari_ini(user)
    elif m == "Perangkat Pembelajaran": halaman_perangkat(user)
    elif m == "PR": halaman_pr(user)
    elif m == "Tugas": halaman_tugas(user)
    elif m == "Jadwal UH/ASLM": halaman_uh(user)
    elif m == "Input Nilai": halaman_nilai(user)
    elif m == "Komunikasi Orang Tua": halaman_wa(user)
    elif m == "Admin Data": halaman_admin()

if __name__ == "__main__":
    main()
