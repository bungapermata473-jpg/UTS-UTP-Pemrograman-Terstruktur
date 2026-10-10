"""Modul validasi: memastikan input dan data presensi valid.

Modul ini sengaja TIDAK mengimpor modul lain di package,
sehingga bisa dijalankan langsung: python presensi/validasi.py
"""
from datetime import datetime  # library standar untuk memeriksa format tanggal

# Status kehadiran yang diizinkan
STATUS_VALID = ("hadir", "izin", "sakit", "alpa")

class DataTidakValidError(Exception):
    """Exception buatan sendiri: dilempar saat data/input tidak valid."""

def validasi_teks(teks, nama_field):
    """Pastikan teks tidak kosong dan tidak mengandung pemisah '|'."""
    teks = teks.strip()
    if not teks:
        raise DataTidakValidError(f"Field '{nama_field}' tidak boleh kosong.")
    if "|" in teks:
        raise DataTidakValidError(f"Field '{nama_field}' tidak boleh berisi karakter '|'.")
    return teks
  
def validasi_nim(teks):
    """NIM harus angka saja, panjang 6 sampai 12 digit."""
    nim = teks.strip()
    if not nim.isdigit():
        raise DataTidakValidError(f"NIM '{teks}' harus berupa angka saja.")
    if not 6 <= len(nim) <= 12:
        raise DataTidakValidError(f"NIM '{nim}' harus 6-12 digit (ditemukan {len(nim)}).")
    return nim

def validasi_tanggal(teks):
    """Pastikan tanggal berformat YYYY-MM-DD dan benar-benar ada di kalender."""
    try:
        datetime.strptime(teks.strip(), "%Y-%m-%d")
    except ValueError:
        raise DataTidakValidError(
            f"Tanggal '{teks}' tidak valid (format harus YYYY-MM-DD).") from None
    return teks.strip()

def validasi_status(teks):
    """Pastikan status ada di STATUS_VALID (tidak peka huruf besar/kecil)."""
    status = teks.strip().lower()
    if status not in STATUS_VALID:
        raise DataTidakValidError(
            f"Status '{teks}' tidak dikenal. Pilihan: {', '.join(STATUS_VALID)}.")
    return status

def validasi_batas(teks):
    """Ubah batas minimum kehadiran (persen) menjadi angka 0-100."""
    try:
        nilai = int(str(teks).strip())
    except ValueError:
        raise DataTidakValidError(f"Batas '{teks}' bukan angka bulat.") from None
    if not 0 <= nilai <= 100:
        raise DataTidakValidError(f"Batas harus antara 0 dan 100 (diterima: {nilai}).")
    return nilai

# Pengujian lokal: hanya jalan jika file ini dieksekusi langsung
if __name__ == "__main__":
    print("== Pengujian lokal validasi.py ==")
    for contoh in ["2517052031", "abc123", "123"]:
        try:
            print(f"NIM {contoh!r} -> OK: {validasi_nim(contoh)}")
        except DataTidakValidError as e:
            print(f"NIM {contoh!r} -> DITOLAK: {e}")
    for contoh in ["hadir", "SAKIT", "bolos"]:
        try:
            print(f"status {contoh!r} -> OK: {validasi_status(contoh)}")
        except DataTidakValidError as e:
            print(f"status {contoh!r} -> DITOLAK: {e}")
    try:
        validasi_tanggal("2026-13-40")
    except DataTidakValidError as e:
        print("tanggal 2026-13-40 -> DITOLAK:", e)
