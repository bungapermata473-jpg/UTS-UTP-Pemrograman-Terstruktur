"""Modul processing: class data dan fungsi perhitungan/analisis presensi."""

from .validasi import (DataTidakValidError, validasi_nim, validasi_status,
                       validasi_tanggal, validasi_teks)

BATAS_MINIMUM = 75  # persen kehadiran minimum


# ---------------------------------------------------------------- fungsi *args
def hitung_hadir(*status):
    """Hitung berapa status 'hadir' dari sejumlah status. *args: jumlah bebas."""
    return len(list(filter(lambda s: s == "hadir", status)))


def hitung_persentase(bagian, total):
    """Persentase bagian/total (0 jika total 0, menghindari pembagian nol)."""
    if total == 0:
        return 0.0
    return round(bagian / total * 100, 1)


# ---------------------------------------------------------------- class 1
class Presensi:
    """Satu catatan kehadiran seorang mahasiswa pada satu pertemuan."""

    def __init__(self, tanggal, nim, nama, status, **tambahan):
        self.tanggal = tanggal
        self.nim = nim
        self.nama = nama
        self.status = status
        # **kwargs: atribut tambahan yang bervariasi (misal nomor_baris)
        self.tambahan = tambahan

    @classmethod
    def dari_baris(cls, baris, **tambahan):
        """Buat objek dari satu baris file 'tanggal|nim|nama|status'."""
        bagian = baris.strip().split("|")
        if len(bagian) != 4:
            raise DataTidakValidError(
                f"Jumlah kolom harus 4, ditemukan {len(bagian)}.")
        tanggal, nim, nama, status = bagian
        # Pemanggilan dengan keyword argument; setiap kolom divalidasi dulu
        return cls(tanggal=validasi_tanggal(tanggal),
                   nim=validasi_nim(nim),
                   nama=validasi_teks(nama, "nama"),
                   status=validasi_status(status),
                   **tambahan)

    def ke_baris(self):
        """Ubah objek menjadi satu baris teks untuk disimpan ke file."""
        return f"{self.tanggal}|{self.nim}|{self.nama}|{self.status}"

    def hadir(self):
        """True jika status 'hadir' (izin/sakit/alpa dihitung tidak hadir)."""
        return self.status == "hadir"

    def __str__(self):
        return f"{self.tanggal} | {self.nim:<12} | {self.nama:<24} | {self.status.upper()}"


# ---------------------------------------------------------------- lambda & helper
def urutkan_presensi(daftar, berdasarkan="tanggal", terbalik=False):
    """Urutkan daftar presensi memakai sorted() dengan lambda sebagai key."""
    kunci = {
        "tanggal": lambda p: p.tanggal,
        "nim": lambda p: p.nim,
        "nama": lambda p: p.nama.lower(),
        "status": lambda p: p.status,
    }
    if berdasarkan not in kunci:
        raise DataTidakValidError(
            f"Urutan '{berdasarkan}' tidak dikenal (pilih: {', '.join(kunci)}).")
    return sorted(daftar, key=kunci[berdasarkan], reverse=terbalik)


def sudah_ada(daftar, tanggal, nim):
    """Cek apakah mahasiswa ini sudah dicatat pada tanggal tersebut."""
    return any(p.tanggal == tanggal and p.nim == nim for p in daftar)


# ---------------------------------------------------------------- class 2
class RekapPresensi:
    """Kumpulan analisis atas daftar objek Presensi."""

    def __init__(self, daftar):
        self.daftar = list(daftar)

    def daftar_status(self):
        """Ambil status saja memakai map() + lambda."""
        return list(map(lambda p: p.status, self.daftar))

    def jumlah_pertemuan(self):
        """Jumlah tanggal pertemuan yang berbeda (pakai set)."""
        return len({p.tanggal for p in self.daftar})

    def jumlah_per_status(self):
        """Dictionary {status: jumlah}."""
        hasil = {}
        for status in self.daftar_status():
            hasil[status] = hasil.get(status, 0) + 1
        # assert: jumlah semua status harus sama dengan jumlah catatan
        assert sum(hasil.values()) == len(self.daftar), "Jumlah status tidak cocok!"
        return hasil

    def persen_kelas(self):
        """Persentase kehadiran seluruh kelas (unpack list ke *args)."""
        return hitung_persentase(hitung_hadir(*self.daftar_status()), len(self.daftar))

    def rekap_per_mahasiswa(self):
        """Dictionary {nim: {nama, hadir, total, persen}}."""
        data = {}
        for p in self.daftar:
            rekap = data.setdefault(p.nim, {"nama": p.nama, "hadir": 0, "total": 0})
            rekap["total"] += 1
            if p.hadir():
                rekap["hadir"] += 1
        for rekap in data.values():
            rekap["persen"] = hitung_persentase(rekap["hadir"], rekap["total"])
            assert 0 <= rekap["persen"] <= 100, "Persentase di luar 0-100!"
        return data

    def di_bawah_batas(self, batas=BATAS_MINIMUM):
        """Daftar (nim, rekap) yang persentasenya < batas (filter() + lambda)."""
        rekap = self.rekap_per_mahasiswa()
        hasil = filter(lambda item: item[1]["persen"] < batas, rekap.items())
        return sorted(hasil, key=lambda item: item[1]["persen"])

    def filter_tanggal(self, tanggal):
        """Semua catatan pada tanggal tertentu."""
        return [p for p in self.daftar if p.tanggal == tanggal]


def buat_teks_rekap(rekap, batas=BATAS_MINIMUM):
    """Susun teks laporan rekap dari objek RekapPresensi."""
    baris = ["=== REKAP PRESENSI KELAS ===",
             f"Jumlah pertemuan : {rekap.jumlah_pertemuan()}",
             f"Jumlah catatan   : {len(rekap.daftar)}",
             f"Kehadiran kelas  : {rekap.persen_kelas()}%",
             "", "Jumlah per status:"]
    for status, jumlah in sorted(rekap.jumlah_per_status().items()):
        baris.append(f"  - {status:<6}: {jumlah}")
    baris.append(f"\nRekap per mahasiswa (batas minimum {batas}%):")
    baris.append(f"  {'NIM':<14}{'Nama':<26}{'Hadir':<8}{'Persen':<9}Keterangan")
    for nim, data in sorted(rekap.rekap_per_mahasiswa().items()):
        ket = "PERLU PERHATIAN" if data["persen"] < batas else "Aman"
        hadir = f"{data['hadir']}/{data['total']}"
        baris.append(f"  {nim:<14}{data['nama']:<26}{hadir:<8}{str(data['persen']) + '%':<9}{ket}")
    return "\n".join(baris) + "\n"
