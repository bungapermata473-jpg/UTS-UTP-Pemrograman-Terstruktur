import unittest
from suhu import analisis, hitung_rata_rata, tentukan_kategori

DATA = [
    {"hari": "Senin", "suhu": 31}, {"hari": "Selasa", "suhu": 33},
    {"hari": "Rabu", "suhu": 29}, {"hari": "Kamis", "suhu": 35},
    {"hari": "Jumat", "suhu": 32}, {"hari": "Sabtu", "suhu": 30},
    {"hari": "Minggu", "suhu": 28},
]

class TestAnalisis(unittest.TestCase):
    def test_rata_rata(self):
        hasil = analisis(DATA)
        self.assertAlmostEqual(hasil["rata_rata"], 218 / 7)

    def test_tertinggi_dan_terendah(self):
        hasil = analisis(DATA)
        self.assertEqual(hasil["tertinggi"], {"hari": "Kamis", "suhu": 35})
        self.assertEqual(hasil["terendah"], {"hari": "Minggu", "suhu": 28})

    def test_jumlah_hari_panas(self):
        self.assertEqual(analisis(DATA)["jumlah_panas"], 3)

    def test_batas_kategori(self):
        self.assertEqual(tentukan_kategori(32), "Panas")    
        self.assertEqual(tentukan_kategori(31), "Normal")

    def test_data_kosong(self):
        with self.assertRaises(ValueError):
            analisis([])

if __name__ == "__main__":
    unittest.main()
