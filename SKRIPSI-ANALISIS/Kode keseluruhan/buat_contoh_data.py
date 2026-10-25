"""Membuat file contoh 'contoh_data_transaksi.xlsx' (data sintetis, hanya untuk uji coba sistem).

Jalankan:  python buat_contoh_data.py
Data asli Toko Sembiring Sembako tetap diunggah lewat halaman Kelola Data.
"""
import random
from datetime import date, timedelta

import pandas as pd

random.seed(7)
# (produk, harga, peluang muncul) - mengikuti produk teratas pada Tabel 4.7 skripsi
PRODUK = [("Aqua", 4000, .32), ("Plastik Cendana", 6000, .31), ("Plastik Teko", 7000, .29),
          ("Cup", 11000, .24), ("Gula", 18000, .21), ("Tali Plastik", 25000, .18),
          ("Mie Instan", 3500, .17), ("Saos", 9000, .14), ("Minyak Kita", 17000, .13),
          ("Carnation", 12000, .12), ("Rokok", 2500, .11), ("Kecap", 8000, .09),
          ("Tissue", 6000, .09), ("Beras Regar 1 kg", 15000, .09), ("Cater", 1000, .09),
          ("Cappucino", 2000, .08), ("Jajan", 2000, .08), ("Tutup Cup", 4000, .08),
          ("Karet", 1000, .07), ("Garam", 3000, .07)]
# pola yang sengaja dibuat berkaitan agar aturan asosiasi lift > 1 muncul
PAKET = [(["Cup", "Gula", "Minyak Kita"], .07), (["Mie Instan", "Carnation", "Cup"], .05),
         (["Plastik Cendana", "Tali Plastik"], .08), (["Cup", "Tutup Cup"], .04)]

rows, tgl = [], date(2025, 4, 17)
for n in range(1, 1201):
    if n % 4 == 0:
        tgl += timedelta(days=1)
    item = {p for p, _, pr in PRODUK if random.random() < pr * .6}
    for paket, pr in PAKET:
        if random.random() < pr:
            item |= set(paket)
    if not item:
        item = {"Aqua"}
    harga = {p: h for p, h, _ in PRODUK}
    for p in item:
        q = random.choice([1, 1, 1, 2, 3])
        rows.append([f"Trx{n}", tgl.strftime("%d-%m-%y"), p, q, harga[p], q * harga[p]])

df = pd.DataFrame(rows, columns=["No_Transaksi", "Tanggal", "Nama_Produk", "Jumlah", "Harga_Satuan", "Total"])
# sisipkan data "kotor" agar tahap preprocessing terlihat bekerja
kotor = df.sample(25, random_state=1).copy()
kotor["Nama_Produk"] = ["royko besar", "AQUA", " gula ", "cup", "Rokok"] * 5
df = pd.concat([df, kotor, df.sample(15, random_state=2)], ignore_index=True)
df.loc[df.sample(6, random_state=3).index, "Nama_Produk"] = None
df.to_excel("contoh_data_transaksi.xlsx", index=False)
print("Selesai:", len(df), "baris ->", "contoh_data_transaksi.xlsx")
