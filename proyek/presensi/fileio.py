"""Modul fileio: semua operasi baca/tulis/tambah file data."""

import os

from .processing import Presensi
from .validasi import DataTidakValidError

HEADER = "# tanggal|nim|nama|status\n"


def buat_file_data(path):
    """Mode 'x': buat file data pertama kali. Gagal jika file sudah ada."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as file:
            file.write(HEADER)
        print(f"[Info] File data baru dibuat: {path}")
        return True
    except FileExistsError:
        # Tujuan mode 'x': jangan sampai data lama tertimpa
        print(f"[Info] File '{path}' sudah ada, data lama tidak ditimpa.")
        return False


def tambah_presensi(path, presensi):
    """Mode 'a': tambahkan satu catatan baru di akhir file."""
    with open(path, "a", encoding="utf-8") as file:
        file.write(presensi.ke_baris() + "\n")


def muat_presensi(path, tampilkan_peringatan=True):
    """Mode 'r': baca file baris demi baris (iteratif).

    Baris rusak DILEWATI (bukan menghentikan program).
    Return: (daftar_presensi, jumlah_baris_rusak)
    """
    daftar, rusak = [], 0
    try:
        with open(path, "r", encoding="utf-8") as file:
            for nomor, baris in enumerate(file, start=1):   # pembacaan iteratif
                if not baris.strip() or baris.startswith("#"):
                    continue                                 # lewati kosong/komentar
                try:
                    daftar.append(Presensi.dari_baris(baris, nomor_baris=nomor))
                except DataTidakValidError as error:
                    rusak += 1
                    if tampilkan_peringatan:
                        print(f"  [Dilewati] baris {nomor}: {error}")
    except FileNotFoundError:
        print(f"[Error] File data '{path}' belum ada. "
              f"Jalankan ulang program agar file dibuat otomatis.")
    return daftar, rusak


def tulis_laporan(path, teks):
    """Mode 'w': tulis laporan (menimpa laporan sebelumnya)."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(teks)
