BATAS_LULUS = 70

def hitung_rata_rata(*nilai):
    if not nilai:
        raise ValueError("Daftar nilai tidak boleh kosong")
    return sum(float(n) for n in nilai) / len(nilai)

def tentukan_status(rata, batas=BATAS_LULUS):
    return "Lulus" if rata >= batas else "Tidak Lulus"

def tampilkan_hasil(nama, daftar_nilai, batas=BATAS_LULUS):
    rata = hitung_rata_rata(*daftar_nilai)
    print("Nama      :", nama)
    print("Rata-rata :", round(rata, 2))
    print("Status    :", tentukan_status(rata, batas))

if __name__ == "__main__":
    assert round(hitung_rata_rata(80, 75, 90), 2) == 81.67
    assert hitung_rata_rata(60, 65, 55, 70) == 62.5
    assert tentukan_status(62.5) == "Tidak Lulus"
    assert tentukan_status(62.5, batas=60) == "Lulus"
    print("Semua pengujian berhasil")
