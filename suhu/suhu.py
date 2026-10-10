def baca_data(nama_file):
    data = []
    try:
        with open(nama_file, "r") as file:
            for baris in file:
                baris = baris.strip()
                if not baris:
                    continue
                try:
                    hari, suhu = baris.split(";")
                    data.append({"hari": hari, "suhu": int(suhu)})
                except ValueError:
                    print("Baris dilewati (data tidak valid):", baris)
    except FileNotFoundError:
        print("Error: file", nama_file, "tidak ditemukan")
    return data

def hitung_rata_rata(*suhu):
    if not suhu:
        raise ValueError("Data suhu tidak boleh kosong")
    return sum(suhu) / len(suhu)

def tentukan_kategori(suhu, batas=32):
    return "Panas" if suhu >= batas else "Normal"

def analisis(data, batas=32):
    if not data:
        raise ValueError("Data suhu tidak boleh kosong")

    rata = hitung_rata_rata(*[d["suhu"] for d in data])
    tertinggi = max(data, key=lambda d: d["suhu"])
    terendah = min(data, key=lambda d: d["suhu"])
    detail = [
        {**d, "kategori": tentukan_kategori(d["suhu"], batas=batas)}
        for d in data
    ]
    jumlah_panas = len([d for d in detail if d["kategori"] == "Panas"])

    return {
        "detail": detail,
        "rata_rata": rata,
        "tertinggi": tertinggi,
        "terendah": terendah,
        "jumlah_panas": jumlah_panas,
    }

def tulis_laporan(hasil, nama_file="laporan_suhu.txt"):
    baris = ["LAPORAN SUHU MINGGUAN", "=" * 32]
    for d in hasil["detail"]:
        baris.append(f"{d['hari']:<8}: {d['suhu']} C ({d['kategori']})")
    baris.append("-" * 32)
    baris.append(f"Rata-rata suhu    : {hasil['rata_rata']:.2f} C")
    baris.append(f"Suhu tertinggi    : {hasil['tertinggi']['suhu']} C ({hasil['tertinggi']['hari']})")
    baris.append(f"Suhu terendah     : {hasil['terendah']['suhu']} C ({hasil['terendah']['hari']})")
    baris.append(f"Jumlah hari Panas : {hasil['jumlah_panas']} hari")

    with open(nama_file, "w") as file:
        file.write("\n".join(baris) + "\n")

    with open(nama_file, "r") as file:
        print(file.read())

def main():
    data = baca_data("suhu.txt")
    if not data:
        return
    hasil = analisis(data, batas=32)
    tulis_laporan(hasil)

if __name__ == "__main__":
    main()
