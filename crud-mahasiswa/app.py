"""Aplikasi CRUD Data Mahasiswa (Flask + SQLite)."""
import os
import sqlite3
from datetime import datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "mahasiswa.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "ganti-dengan-kunci-rahasia"  # dipakai untuk flash message
app.config["DATABASE"] = DATABASE


# ---------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nim           INTEGER NOT NULL UNIQUE,
            nama          TEXT    NOT NULL,
            program_studi TEXT    NOT NULL,
            angkatan      INTEGER NOT NULL,
            ipk           REAL    NOT NULL CHECK (ipk >= 0 AND ipk <= 4)
        )
        """
    )
    db.commit()
    db.close()


# --------------------------------------------------------------- helpers
def tahun_sekarang():
    return datetime.now().year


def lama_studi(angkatan):
    """Lama Studi (tahun) = tahun sekarang - angkatan (dihitung otomatis)."""
    return tahun_sekarang() - angkatan


app.jinja_env.globals["lama_studi"] = lama_studi


def validasi(form, id_sendiri=None):
    """Validasi input form. Mengembalikan (data, daftar_error)."""
    errors = []
    nim_raw = form.get("nim", "").strip()
    nama = form.get("nama", "").strip()
    prodi = form.get("program_studi", "").strip()
    angkatan_raw = form.get("angkatan", "").strip()
    ipk_raw = form.get("ipk", "").strip().replace(",", ".")

    nim = angkatan = ipk = None

    if not nim_raw:
        errors.append("NIM wajib diisi.")
    else:
        try:
            nim = int(nim_raw)
            if nim <= 0:
                raise ValueError
        except ValueError:
            errors.append("NIM harus berupa angka bulat positif.")

    if not nama:
        errors.append("Nama wajib diisi.")
    if not prodi:
        errors.append("Program studi wajib diisi.")

    if not angkatan_raw:
        errors.append("Angkatan wajib diisi.")
    else:
        try:
            angkatan = int(angkatan_raw)
            if not 1900 <= angkatan <= tahun_sekarang():
                errors.append(f"Angkatan harus antara 1900 dan {tahun_sekarang()}.")
        except ValueError:
            errors.append("Angkatan harus berupa angka bulat (contoh: 2023).")

    if not ipk_raw:
        errors.append("IPK wajib diisi.")
    else:
        try:
            ipk = float(ipk_raw)
            if not 0.00 <= ipk <= 4.00:
                errors.append("IPK harus berada di rentang 0.00 - 4.00.")
        except ValueError:
            errors.append("IPK harus berupa angka (contoh: 3.75).")

    # NIM harus unik (saat tambah, atau saat ubah ke NIM milik orang lain)
    if nim is not None:
        row = get_db().execute(
            "SELECT id FROM mahasiswa WHERE nim = ?", (nim,)
        ).fetchone()
        if row is not None and row["id"] != id_sendiri:
            errors.append(f"NIM {nim} sudah terdaftar.")

    data = {
        "nim": nim_raw,
        "nama": nama,
        "program_studi": prodi,
        "angkatan": angkatan_raw,
        "ipk": ipk_raw,
    }
    if not errors:
        data.update(nim=nim, angkatan=angkatan, ipk=ipk)
    return data, errors


def ambil_atau_404(id_):
    row = get_db().execute("SELECT * FROM mahasiswa WHERE id = ?", (id_,)).fetchone()
    if row is None:
        from flask import abort

        abort(404)
    return row


# ---------------------------------------------------------------- routes
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT * FROM mahasiswa WHERE CAST(nim AS TEXT) LIKE ? OR nama LIKE ? "
            "OR program_studi LIKE ? ORDER BY nim",
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()
    return render_template("index.html", rows=rows, q=q, tahun=tahun_sekarang())


@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        data, errors = validasi(request.form)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html", mode="tambah", m=data), 400
        db = get_db()
        db.execute(
            "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) "
            "VALUES (?, ?, ?, ?, ?)",
            (data["nim"], data["nama"], data["program_studi"], data["angkatan"], data["ipk"]),
        )
        db.commit()
        flash(f"Mahasiswa {data['nama']} berhasil ditambahkan.", "ok")
        return redirect(url_for("index"))
    return render_template("form.html", mode="tambah", m={})


@app.route("/mahasiswa/<int:id_>")
def detail(id_):
    return render_template("detail.html", m=ambil_atau_404(id_))


@app.route("/mahasiswa/<int:id_>/ubah", methods=["GET", "POST"])
def ubah(id_):
    row = ambil_atau_404(id_)
    if request.method == "POST":
        data, errors = validasi(request.form, id_sendiri=id_)
        if errors:
            for e in errors:
                flash(e, "error")
            data["id"] = id_
            return render_template("form.html", mode="ubah", m=data), 400
        db = get_db()
        db.execute(
            "UPDATE mahasiswa SET nim=?, nama=?, program_studi=?, angkatan=?, ipk=? "
            "WHERE id=?",
            (data["nim"], data["nama"], data["program_studi"], data["angkatan"], data["ipk"], id_),
        )
        db.commit()
        flash(f"Data {data['nama']} berhasil diperbarui.", "ok")
        return redirect(url_for("detail", id_=id_))
    return render_template("form.html", mode="ubah", m=dict(row))


@app.route("/mahasiswa/<int:id_>/hapus", methods=["POST"])
def hapus(id_):
    row = ambil_atau_404(id_)
    db = get_db()
    db.execute("DELETE FROM mahasiswa WHERE id = ?", (id_,))
    db.commit()
    flash(f"Data {row['nama']} berhasil dihapus.", "ok")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
