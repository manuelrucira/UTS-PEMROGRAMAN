"""Tes otomatis sederhana untuk aplikasi CRUD mahasiswa."""
import os
import tempfile

import pytest

import app as app_module


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    app_module.app.config["DATABASE"] = path
    app_module.app.config["TESTING"] = True
    app_module.init_db()
    with app_module.app.test_client() as c:
        yield c
    os.remove(path)


VALID = {"nim": "24010001", "nama": "Budi", "program_studi": "Bisnis Digital",
         "angkatan": "2023", "ipk": "3.75"}


def test_create_and_read_with_lama_studi(client):
    r = client.post("/tambah", data=VALID, follow_redirects=True)
    assert b"berhasil ditambahkan" in r.data
    tahun = app_module.tahun_sekarang()
    assert str(tahun - 2023).encode() in r.data
    assert b"Budi" in r.data


@pytest.mark.parametrize("field", ["nim", "nama", "program_studi"])
def test_required_fields(client, field):
    data = {**VALID, field: ""}
    r = client.post("/tambah", data=data)
    assert r.status_code == 400 and b"wajib diisi" in r.data


@pytest.mark.parametrize("ipk", ["-0.1", "4.01", "abc"])
def test_ipk_range(client, ipk):
    r = client.post("/tambah", data={**VALID, "ipk": ipk})
    assert r.status_code == 400 and b"IPK" in r.data


def test_duplicate_nim(client):
    client.post("/tambah", data=VALID)
    r = client.post("/tambah", data={**VALID, "nama": "Lain"})
    assert r.status_code == 400 and b"sudah terdaftar" in r.data


def test_update_and_delete(client):
    client.post("/tambah", data=VALID)
    r = client.post("/mahasiswa/1/ubah", data={**VALID, "nama": "Budi S", "ipk": "3.9"},
                    follow_redirects=True)
    assert b"Budi S" in r.data and b"3.90" in r.data
    r = client.post("/mahasiswa/1/hapus", follow_redirects=True)
    assert b"berhasil dihapus" in r.data and b"Belum ada data" in r.data


def test_update_to_other_nim_rejected(client):
    client.post("/tambah", data=VALID)
    client.post("/tambah", data={**VALID, "nim": "24010002"})
    r = client.post("/mahasiswa/2/ubah", data=VALID)
    assert r.status_code == 400 and b"sudah terdaftar" in r.data
