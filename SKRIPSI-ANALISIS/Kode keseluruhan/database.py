"""Lapisan database SQLite - sesuai Bab 4.2.5 Desain Database skripsi.

Empat tabel: users, transactions, analysis_results, comparison_recommendations.
"""
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from datetime import datetime

DB_PATH = os.environ.get("SEMBAKO_DB") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sembako.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL UNIQUE CHECK (length(username) <= 10),
    password_hash  TEXT NOT NULL CHECK (length(password_hash) <= 255)
);
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    no_transaksi   TEXT NOT NULL CHECK (length(no_transaksi) <= 8),
    tanggal        TEXT NOT NULL CHECK (length(tanggal) = 10),
    nama_produk    TEXT NOT NULL CHECK (length(nama_produk) <= 50),
    jumlah         INTEGER NOT NULL CHECK (jumlah > 0),
    harga_satuan   REAL NOT NULL CHECK (harga_satuan >= 0),
    total          REAL NOT NULL CHECK (total >= 0),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS analysis_results (
    analysis_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_code        TEXT NOT NULL CHECK (length(comparison_code) <= 6),
    nama_algoritma         TEXT NOT NULL CHECK (nama_algoritma IN ('Apriori','FP-Growth')),
    minimum_support        REAL NOT NULL CHECK (minimum_support BETWEEN 0.5 AND 20),
    minimum_confidence     REAL NOT NULL,
    minimum_lift           REAL NOT NULL,
    jumlah_frequent_itemset INTEGER NOT NULL,
    jumlah_aturan_asosiasi INTEGER NOT NULL,
    waktu_eksekusi         REAL NOT NULL,
    data_frequent_itemset  TEXT NOT NULL,
    data_aturan_asosiasi   TEXT NOT NULL,
    tanggal_analisis       TEXT NOT NULL CHECK (length(tanggal_analisis) = 19)
);
CREATE TABLE IF NOT EXISTS comparison_recommendations (
    result_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id        INTEGER NOT NULL,
    comparison_code    TEXT NOT NULL CHECK (length(comparison_code) <= 6),
    jenis_hasil        TEXT NOT NULL CHECK (jenis_hasil IN ('Perbandingan','Rekomendasi')),
    judul              TEXT NOT NULL,
    deskripsi          TEXT NOT NULL,
    algoritma_tercepat TEXT CHECK (algoritma_tercepat IN ('Apriori','FP-Growth')),
    tanggal_dibuat     TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(analysis_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_trx_no ON transactions(no_transaksi);
CREATE INDEX IF NOT EXISTS idx_ar_code ON analysis_results(comparison_code);
"""


class InitialCredentialsRequired(RuntimeError):
    pass


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def now_iso():
    return datetime.now().isoformat(timespec="seconds")  # 19 karakter


# ---------------------------------------------------------------- users
def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${dk}"


def init_db(initial_user: str | None = None, initial_pass: str | None = None):
    with conn() as c:
        c.executescript(SCHEMA)
        if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            initial_user = initial_user or os.environ.get("APP_USER")
            initial_pass = initial_pass or os.environ.get("APP_PASS")
            if not initial_user or not initial_pass:
                raise InitialCredentialsRequired(
                    "Atur APP_USER dan APP_PASS sebelum membuat database pertama kali."
                )
            c.execute("INSERT INTO users(username, password_hash) VALUES (?,?)",
                      (initial_user[:10], hash_password(initial_pass)))


def verify_user(username: str, password: str):
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (username.strip(),)).fetchone()
    if not row:
        return None
    salt = row["password_hash"].split("$")[0]
    if hmac.compare_digest(hash_password(password, salt), row["password_hash"]):
        return dict(row)
    return None


# --------------------------------------------------------- transactions
def existing_transaction_numbers() -> set:
    with conn() as c:
        return {r[0] for r in c.execute("SELECT DISTINCT no_transaksi FROM transactions")}


def insert_transactions(df, user_id: int) -> int:
    rows = [(user_id, r.no_transaksi, r.tanggal, r.nama_produk, int(r.jumlah),
             float(r.harga_satuan), float(r.total)) for r in df.itertuples(index=False)]
    with conn() as c:
        c.executemany(
            "INSERT INTO transactions(user_id,no_transaksi,tanggal,nama_produk,jumlah,harga_satuan,total)"
            " VALUES (?,?,?,?,?,?,?)", rows)
    return len(rows)


def get_transactions(start: str | None = None, end: str | None = None):
    import pandas as pd
    q, p = "SELECT no_transaksi,tanggal,nama_produk,jumlah,harga_satuan,total FROM transactions", []
    if start and end:
        q += " WHERE tanggal BETWEEN ? AND ?"
        p = [start, end]
    q += " ORDER BY tanggal, transaction_id"
    with conn() as c:
        return pd.read_sql_query(q, c, params=p)


def transaction_stats():
    with conn() as c:
        r = c.execute("SELECT COUNT(DISTINCT no_transaksi) t, COUNT(DISTINCT nama_produk) p, COUNT(*) b,"
                      " MIN(tanggal) a, MAX(tanggal) z FROM transactions").fetchone()
    return dict(r)


def delete_transactions_by_no(no_list) -> int:
    with conn() as c:
        cur = c.executemany("DELETE FROM transactions WHERE no_transaksi=?", [(n,) for n in no_list])
        return cur.rowcount


def delete_transactions_by_period(start: str, end: str) -> int:
    with conn() as c:
        return c.execute("DELETE FROM transactions WHERE tanggal BETWEEN ? AND ?", (start, end)).rowcount


def delete_all_transactions() -> int:
    with conn() as c:
        return c.execute("DELETE FROM transactions").rowcount


# ------------------------------------------------------------- analysis
def save_analysis(code, algo, support_pct, conf_pct, lift, n_freq, n_rules, seconds,
                  freq_payload, rules_payload) -> int:
    with conn() as c:
        cur = c.execute(
            "INSERT INTO analysis_results(comparison_code,nama_algoritma,minimum_support,minimum_confidence,"
            "minimum_lift,jumlah_frequent_itemset,jumlah_aturan_asosiasi,waktu_eksekusi,data_frequent_itemset,"
            "data_aturan_asosiasi,tanggal_analisis) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (code, algo, support_pct, conf_pct, lift, n_freq, n_rules, seconds,
             json.dumps(freq_payload, ensure_ascii=False), json.dumps(rules_payload, ensure_ascii=False),
             now_iso()))
        return cur.lastrowid


def save_comparison_result(analysis_id, code, jenis, judul, deskripsi, tercepat=None):
    with conn() as c:
        c.execute("INSERT INTO comparison_recommendations(analysis_id,comparison_code,jenis_hasil,judul,"
                  "deskripsi,algoritma_tercepat,tanggal_dibuat) VALUES (?,?,?,?,?,?,?)",
                  (analysis_id, code, jenis, judul, deskripsi, tercepat, now_iso()))


def _decode(row):
    if row is None:
        return None
    d = dict(row)
    d["freq"] = json.loads(d["data_frequent_itemset"])
    d["rules"] = json.loads(d["data_aturan_asosiasi"])
    return d


def get_analysis(analysis_id):
    with conn() as c:
        return _decode(c.execute("SELECT * FROM analysis_results WHERE analysis_id=?", (analysis_id,)).fetchone())


def get_analysis_by_code(code):
    with conn() as c:
        rows = c.execute("SELECT * FROM analysis_results WHERE comparison_code=?", (code,)).fetchall()
    return {r["nama_algoritma"]: _decode(r) for r in rows}


def latest_code():
    with conn() as c:
        r = c.execute("SELECT comparison_code FROM analysis_results ORDER BY analysis_id DESC LIMIT 1").fetchone()
    return r[0] if r else None


def list_codes():
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT comparison_code, MIN(minimum_support) sup, MAX(tanggal_analisis) tgl, COUNT(*) n"
            " FROM analysis_results GROUP BY comparison_code ORDER BY MAX(analysis_id) DESC")]


def list_history(search: str = "", limit: int = 10, offset: int = 0):
    like = f"%{search.strip()}%"
    where = ("WHERE nama_algoritma LIKE ? OR tanggal_analisis LIKE ? OR comparison_code LIKE ?"
             " OR CAST(minimum_support AS TEXT) LIKE ?") if search.strip() else ""
    p = [like] * 4 if search.strip() else []
    with conn() as c:
        total = c.execute(f"SELECT COUNT(*) FROM analysis_results {where}", p).fetchone()[0]
        rows = c.execute(
            "SELECT analysis_id,comparison_code,nama_algoritma,minimum_support,minimum_confidence,minimum_lift,"
            f"jumlah_frequent_itemset,jumlah_aturan_asosiasi,waktu_eksekusi,tanggal_analisis FROM analysis_results {where}"
            " ORDER BY analysis_id DESC LIMIT ? OFFSET ?", p + [limit, offset]).fetchall()
    return [dict(r) for r in rows], total


def all_analysis_summary():
    import pandas as pd
    with conn() as c:
        return pd.read_sql_query(
            "SELECT analysis_id,comparison_code,nama_algoritma,minimum_support,jumlah_frequent_itemset,"
            "jumlah_aturan_asosiasi,waktu_eksekusi,tanggal_analisis FROM analysis_results ORDER BY analysis_id", c)


def get_results(code, jenis):
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM comparison_recommendations WHERE comparison_code=? AND jenis_hasil=? ORDER BY result_id",
            (code, jenis))]


def delete_analysis(analysis_id) -> int:
    with conn() as c:  # rekomendasi/perbandingan ikut terhapus (ON DELETE CASCADE)
        return c.execute("DELETE FROM analysis_results WHERE analysis_id=?", (analysis_id,)).rowcount


def delete_all_analysis() -> int:
    with conn() as c:
        return c.execute("DELETE FROM analysis_results").rowcount


def dashboard_stats():
    with conn() as c:
        trx = c.execute("SELECT COUNT(DISTINCT no_transaksi) FROM transactions").fetchone()[0]
        n = c.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
        last = c.execute("SELECT * FROM analysis_results ORDER BY analysis_id DESC LIMIT 1").fetchone()
    return {"transaksi": trx, "analisis": n, "last": dict(last) if last else None}
