"""Program utama: Presensi Kelas.

Jalankan dari folder proyek:  python main.py
"""

from datetime import date  # library untuk tanggal hari ini

from presensi.fileio import (buat_file_data, muat_presensi, tambah_presensi,
                             tulis_laporan)
from presensi.processing import (BATAS_MINIMUM, Presensi, RekapPresensi,
                                 buat_teks_rekap, sudah_ada, urutkan_presensi)
from presensi.validasi import (STATUS_VALID, DataTidakValidError,
                               validasi_batas, validasi_nim, validasi_status,
                               validasi_tanggal, validasi_teks)

FILE_DATA = "data/presensi.txt"
FILE_LAPORAN = "data/rekap_presensi.txt"


def menu_catat():
    """Minta input pengguna, validasi, cek duplikat, lalu simpan ke file."""
    try:
        tanggal = input("Tanggal (YYYY-MM-DD, kosong = hari ini): ").strip()
        tanggal = validasi_tanggal(tanggal or date.today().isoformat())
        nim = validasi_nim(input("NIM: "))
        nama = validasi_teks(input("Nama: "), "nama")
        print("Status:", ", ".join(STATUS_VALID))
        status = validasi_status(input("Status: "))
    except DataTidakValidError as error:
        print(f"[Input ditolak] {error}")
        return
    daftar, _ = muat_presensi(FILE_DATA, tampilkan_peringatan=False)
    if sudah_ada(daftar, tanggal, nim):
        print(f"[Ditolak] NIM {nim} sudah dicatat pada {tanggal}.")
        return
    presensi = Presensi(tanggal=tanggal, nim=nim, nama=nama, status=status)
    tambah_presensi(FILE_DATA, presensi)
    print("Tersimpan:", presensi)


def menu_lihat():
    """Tampilkan semua data, urut sesuai pilihan pengguna."""
    daftar, rusak = muat_presensi(FILE_DATA)
    if not daftar:
        print("Belum ada data.")
        return
    urutan = input("Urutkan berdasarkan (tanggal/nim/nama/status) [tanggal]: ").strip() or "tanggal"
    try:
        # keyword argument saat memanggil fungsi
        hasil = urutkan_presensi(daftar, berdasarkan=urutan, terbalik=False)
    except DataTidakValidError as error:
        print(f"[Error] {error}")
        return
    for p in hasil:
        print(" ", p)
    if rusak:
        print(f"({rusak} baris rusak dilewati)")


def menu_per_tanggal():
    """Tampilkan presensi pada satu tanggal tertentu."""
    daftar, _ = muat_presensi(FILE_DATA, tampilkan_peringatan=False)
    try:
        tanggal = validasi_tanggal(input("Tanggal (YYYY-MM-DD): "))
    except DataTidakValidError as error:
        print(f"[Input ditolak] {error}")
        return
    hasil = RekapPresensi(daftar).filter_tanggal(tanggal)
    if not hasil:
        print(f"Tidak ada data pada {tanggal}.")
    for p in hasil:
        print(" ", p)


def menu_rekap(simpan=False):
    """Tampilkan rekap; jika simpan=True, tulis juga ke file."""
    daftar, _ = muat_presensi(FILE_DATA)
    if not daftar:
        print("Belum ada data untuk direkap.")
        return
    try:
        teks_batas = input(f"Batas minimum kehadiran % (kosong = {BATAS_MINIMUM}): ").strip()
        batas = validasi_batas(teks_batas) if teks_batas else BATAS_MINIMUM
    except DataTidakValidError as error:
        print(f"[Input ditolak] {error}")
        return
    teks = buat_teks_rekap(RekapPresensi(daftar), batas=batas)
    print(teks)
    if simpan:
        tulis_laporan(FILE_LAPORAN, teks)
        print(f"Rekap disimpan ke {FILE_LAPORAN}")


def main():
    buat_file_data(FILE_DATA)  # aman: tidak menimpa jika sudah ada
    menu = {"1": ("Catat presensi", menu_catat),
            "2": ("Lihat semua data", menu_lihat),
            "3": ("Lihat presensi per tanggal", menu_per_tanggal),
            "4": ("Rekap kehadiran", menu_rekap),
            "5": ("Simpan rekap ke file", lambda: menu_rekap(simpan=True))}
    while True:
        print("\n=== PRESENSI KELAS ===")
        for kunci, (nama, _) in menu.items():
            print(f"{kunci}. {nama}")
        print("0. Keluar")
        pilihan = input("Pilih: ").strip()
        if pilihan == "0":
            print("Sampai jumpa!")
            break
        if pilihan in menu:
            menu[pilihan][1]()
        else:
            print("Pilihan tidak tersedia.")


if __name__ == "__main__":
    main()
