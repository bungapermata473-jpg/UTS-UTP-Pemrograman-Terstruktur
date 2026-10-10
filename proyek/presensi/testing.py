"""Modul testing: unit test memakai library unittest.

Jalankan dari folder proyek:  python -m unittest presensi.testing -v
"""

import contextlib
import io
import os
import tempfile
import unittest

from . import fileio
from .processing import (Presensi, RekapPresensi, hitung_hadir,
                         hitung_persentase, sudah_ada, urutkan_presensi)
from .validasi import (DataTidakValidError, validasi_batas, validasi_nim,
                       validasi_status, validasi_tanggal, validasi_teks)


def _buat(tanggal, nim, status, nama="Tes"):
    """Helper kecil untuk membuat objek Presensi di test."""
    return Presensi(tanggal=tanggal, nim=nim, nama=nama, status=status)


class TestValidasi(unittest.TestCase):
    def test_nim_valid(self):
        self.assertEqual(validasi_nim(" 2517052031 "), "2517052031")

    def test_nim_bukan_angka_atau_terlalu_pendek(self):
        with self.assertRaises(DataTidakValidError):
            validasi_nim("abc123")
        with self.assertRaises(DataTidakValidError):
            validasi_nim("123")

    def test_tanggal_valid_dan_salah(self):
        self.assertEqual(validasi_tanggal("2026-10-05"), "2026-10-05")
        with self.assertRaises(DataTidakValidError):
            validasi_tanggal("2026-02-30")

    def test_status_dan_teks_kosong(self):
        self.assertEqual(validasi_status("HADIR"), "hadir")
        with self.assertRaises(DataTidakValidError):
            validasi_status("bolos")
        with self.assertRaises(DataTidakValidError):
            validasi_teks("   ", "nama")

    def test_batas_valid_dan_salah(self):
        self.assertEqual(validasi_batas("80"), 80)
        with self.assertRaises(DataTidakValidError):
            validasi_batas("seratus")
        with self.assertRaises(DataTidakValidError):
            validasi_batas("150")


class TestProcessing(unittest.TestCase):
    def setUp(self):
        self.data = [_buat("2026-10-01", "1111111", "hadir", "Ani"),
                     _buat("2026-10-02", "1111111", "hadir", "Ani"),
                     _buat("2026-10-01", "2222222", "alpa", "Budi"),
                     _buat("2026-10-02", "2222222", "izin", "Budi")]
        self.rekap = RekapPresensi(self.data)

    def test_hitung_hadir_args_dan_persentase(self):
        self.assertEqual(hitung_hadir("hadir", "izin", "hadir"), 2)
        self.assertEqual(hitung_persentase(1, 4), 25.0)
        self.assertEqual(hitung_persentase(0, 0), 0.0)

    def test_rekap_per_mahasiswa(self):
        hasil = self.rekap.rekap_per_mahasiswa()
        self.assertEqual(hasil["1111111"]["persen"], 100.0)
        self.assertEqual(hasil["2222222"]["persen"], 0.0)

    def test_jumlah_per_status_dan_pertemuan(self):
        self.assertEqual(self.rekap.jumlah_per_status(),
                         {"hadir": 2, "alpa": 1, "izin": 1})
        self.assertEqual(self.rekap.jumlah_pertemuan(), 2)

    def test_di_bawah_batas(self):
        hasil = self.rekap.di_bawah_batas(batas=75)
        self.assertEqual([nim for nim, _ in hasil], ["2222222"])

    def test_urutkan_dan_sudah_ada(self):
        hasil = urutkan_presensi(self.data, berdasarkan="nama", terbalik=True)
        self.assertEqual(hasil[0].nama, "Budi")
        with self.assertRaises(DataTidakValidError):
            urutkan_presensi(self.data, berdasarkan="warna")
        self.assertTrue(sudah_ada(self.data, "2026-10-01", "1111111"))
        self.assertFalse(sudah_ada(self.data, "2026-10-09", "1111111"))


class TestFileIO(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "data.txt")

    def tearDown(self):
        self.folder.cleanup()

    def test_mode_x_tidak_menimpa_file(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(fileio.buat_file_data(self.path))
            self.assertFalse(fileio.buat_file_data(self.path))   # FileExistsError ditangani

    def test_tambah_lalu_muat(self):
        with contextlib.redirect_stdout(io.StringIO()):
            fileio.buat_file_data(self.path)
            fileio.tambah_presensi(self.path, _buat("2026-10-05", "2517052031", "sakit", "Bunga"))
            daftar, rusak = fileio.muat_presensi(self.path)
        self.assertEqual((len(daftar), rusak), (1, 0))
        self.assertEqual(daftar[0].status, "sakit")

    def test_baris_rusak_dilewati(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("2026-10-01|2517052031|Bunga|hadir\n")
            file.write("2026-10-02|2517052031|Bunga|bolos\n")   # status rusak
            file.write("baris ngawur\n")                         # kolom kurang
        with contextlib.redirect_stdout(io.StringIO()):
            daftar, rusak = fileio.muat_presensi(self.path)
        self.assertEqual((len(daftar), rusak), (1, 2))

    def test_file_tidak_ada_tidak_crash(self):
        with contextlib.redirect_stdout(io.StringIO()) as keluaran:
            daftar, rusak = fileio.muat_presensi(os.path.join(self.folder.name, "tidak_ada.txt"))
        self.assertEqual((daftar, rusak), ([], 0))
        self.assertIn("belum ada", keluaran.getvalue())

    def test_tulis_laporan_mode_w(self):
        fileio.tulis_laporan(self.path, "lama\n")
        fileio.tulis_laporan(self.path, "baru\n")            # menimpa
        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "baru\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
