"""Preprocessing data sesuai Bab 4.3 (KDD): pembersihan, standarisasi nama produk, one-hot encoding."""
import re
import warnings

import pandas as pd

REQUIRED = ["no_transaksi", "tanggal", "nama_produk", "jumlah", "harga_satuan", "total"]
TAMPIL = {"no_transaksi": "No_Transaksi", "tanggal": "Tanggal", "nama_produk": "Nama_Produk",
          "jumlah": "Jumlah", "harga_satuan": "Harga_Satuan", "total": "Total"}

# Variasi tulisan tangan -> nama baku (tambahkan sesuai kebutuhan toko)
ALIAS = {
    "royko": "Royco", "royko besar": "Royco", "royko kecil": "Royco",
    "royco": "Royco", "royco besar": "Royco", "royco kecil": "Royco",
}


def _norm_col(c) -> str:
    c = re.sub(r"[^a-z]", "", str(c).lower())
    return {"notransaksi": "no_transaksi", "notrx": "no_transaksi", "tanggal": "tanggal",
            "namaproduk": "nama_produk", "produk": "nama_produk", "jumlah": "jumlah", "qty": "jumlah",
            "hargasatuan": "harga_satuan", "harga": "harga_satuan", "total": "total",
            "totalharga": "total"}.get(c, c)


def read_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = [_norm_col(c) for c in df.columns]
    missing = [TAMPIL[c] for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Kolom wajib tidak ditemukan: " + ", ".join(missing))
    return df[REQUIRED].copy()


def standardize_product(name: str) -> str:
    s = re.sub(r"\s+", " ", str(name)).strip()
    s = s.title()
    s = re.sub(r"(\d+)\s*(kg|gr|g|ml|l)\b", lambda m: f"{m.group(1)} {m.group(2).lower()}", s, flags=re.I)
    return ALIAS.get(s.lower(), s)[:50]


def _num(s):
    if not pd.api.types.is_numeric_dtype(s):  # "25.000" atau "25,000" -> 25000
        s = s.astype(str).str.replace(r"[^\d\-,.]", "", regex=True).str.replace(".", "", regex=False) \
              .str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def preprocess(raw: pd.DataFrame):
    """Mengembalikan (data_bersih, statistik). Urutan langkah mengikuti Bab 4.1.2.2 poin 3."""
    df = raw.copy()
    log = {}
    n0 = len(df)

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(subset=["no_transaksi", "nama_produk"])
    log["Nilai kosong (No_Transaksi / Nama_Produk)"] = n0 - len(df)

    df["no_transaksi"] = df["no_transaksi"].astype(str).str.replace(r"[\s.]", "", regex=True)
    df["nama_produk"] = df["nama_produk"].map(standardize_product)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce", dayfirst=True)
    for c in ["jumlah", "harga_satuan", "total"]:
        df[c] = _num(df[c])
    df["total"] = df["total"].fillna(df["jumlah"] * df["harga_satuan"])

    n1 = len(df)
    ok = (df["tanggal"].notna() & (df["jumlah"] > 0) & (df["harga_satuan"] >= 0) & (df["total"] >= 0)
          & (df["no_transaksi"].str.len() <= 8) & (df["nama_produk"].str.len() > 0))
    df = df[ok].copy()
    log["Data tidak valid"] = n1 - len(df)

    df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")
    df["jumlah"] = df["jumlah"].round().astype(int)

    n2 = len(df)
    df = df.drop_duplicates(subset=["no_transaksi", "nama_produk"], keep="first")
    log["Duplikat"] = n2 - len(df)

    n3 = len(df)
    banyak = df.groupby("no_transaksi")["nama_produk"].transform("nunique") > 1
    df = df[banyak]
    log["Transaksi hanya 1 jenis produk"] = n3 - len(df)

    df = df.reset_index(drop=True)
    stats = {
        "total_awal": n0, "total_akhir": len(df), "total_transaksi": df["no_transaksi"].nunique(),
        "total_produk": df["nama_produk"].nunique(), "log": log,
    }
    stats["onehot_shape"] = (stats["total_transaksi"], stats["total_produk"])
    return df, stats


def one_hot(df: pd.DataFrame) -> pd.DataFrame:
    """Matriks biner (baris = transaksi, kolom = produk). Hanya di memori, tidak disimpan ke database."""
    return pd.crosstab(df["no_transaksi"], df["nama_produk"]).gt(0)
