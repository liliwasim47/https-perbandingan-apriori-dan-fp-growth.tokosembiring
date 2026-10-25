"""Mesin data mining: Apriori & FP-Growth (Mlxtend) + struktur FP-Tree dan Conditional Pattern Base (CPB)."""
import math
import time
import uuid
from collections import Counter

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth

MIN_LIFT = 1.0  # aturan valid: lift > 1


# ------------------------------------------------------------------ Apriori / FP-Growth
def _rules(freq: pd.DataFrame, n_trx: int, min_conf: float) -> pd.DataFrame:
    if freq.empty:
        return pd.DataFrame()
    try:
        r = association_rules(freq, num_itemsets=n_trx, metric="confidence", min_threshold=min_conf)
    except TypeError:  # mlxtend versi lama
        r = association_rules(freq, metric="confidence", min_threshold=min_conf)
    return r[r["lift"] > MIN_LIFT].sort_values("lift", ascending=False) if not r.empty else r


def run_algorithm(name: str, basket: pd.DataFrame, min_support: float, min_conf: float) -> dict:
    """min_support & min_conf dalam pecahan (0.05 = 5%). Waktu eksekusi = lama fungsi algoritma berjalan."""
    n = len(basket)
    func = apriori if name == "Apriori" else fpgrowth
    t0 = time.perf_counter()
    freq = func(basket, min_support=min_support, use_colnames=True)
    seconds = time.perf_counter() - t0

    rules = _rules(freq, n, min_conf)
    frequent = sorted(
        ({"itemset": sorted(s), "support": float(sup), "count": int(round(sup * n))}
         for s, sup in zip(freq["itemsets"], freq["support"])),
        key=lambda d: (-d["support"], len(d["itemset"]), d["itemset"]))
    rule_list = [{"antecedent": sorted(r.antecedents), "consequent": sorted(r.consequents),
                  "support": float(r.support), "confidence": float(r.confidence), "lift": float(r.lift)}
                 for r in rules.itertuples()] if not rules.empty else []
    return {"name": name, "frequent": frequent, "rules": rule_list, "seconds": seconds}


def new_code() -> str:
    return uuid.uuid4().hex[:6].upper()  # kode penghubung maks. 6 karakter


# ------------------------------------------------------------------ FP-Tree & CPB
class _Node:
    __slots__ = ("item", "count", "parent", "children")

    def __init__(self, item, parent):
        self.item, self.count, self.parent, self.children = item, 0, parent, {}


def build_fp_structures(basket: pd.DataFrame, min_support: float) -> dict:
    """Bangun Header Table, FP-Tree, dan Conditional Pattern Base (dimulai dari item terakhir header table).

    Urutan item = support menurun (tie: abjad), sama seperti Tabel 4.12-4.13 pada skripsi.
    """
    n = len(basket)
    min_count = max(1, math.ceil(min_support * n - 1e-9))
    trx = [list(basket.columns[row]) for row in basket.to_numpy()]
    counts = Counter(i for t in trx for i in t)
    header = sorted(((i, c) for i, c in counts.items() if c >= min_count), key=lambda x: (-x[1], x[0]))
    order = {i: k for k, (i, _) in enumerate(header)}

    root = _Node(None, None)
    links = {i: [] for i, _ in header}
    for t in trx:
        node = root
        for it in sorted((i for i in t if i in order), key=order.get):
            child = node.children.get(it)
            if child is None:
                child = node.children[it] = _Node(it, node)
                links[it].append(child)
            child.count += 1
            node = child

    def to_dict(nd):
        kids = sorted(nd.children.values(), key=lambda k: (order[k.item]))
        return {"item": nd.item, "count": nd.count, "children": [to_dict(k) for k in kids]}

    cpb, patterns = {}, {}
    for item, total in reversed(header):  # item terakhir -> pertama
        base = []
        for nd in links[item]:
            path, p = [], nd.parent
            while p is not None and p.item is not None:
                path.append(p.item)
                p = p.parent
            if path:
                base.append((path[::-1], nd.count))
        agg = Counter()
        for path, c in base:
            for i in path:
                agg[i] += c
        cpb[item] = {
            "jumlah_node": len(links[item]), "count_item": total,
            "paths": [{"path": p, "count": c} for p, c in base],
            "conditional": [{"item": i, "count": c, "lolos": c >= min_count}
                            for i, c in sorted(agg.items(), key=lambda x: (-x[1], x[0]))],
        }
        found = {}
        _mine(base, (item,), min_count, found)
        found[frozenset([item])] = total
        patterns[item] = [{"itemset": sorted(s), "count": c, "support": c / n}
                          for s, c in sorted(found.items(), key=lambda x: (-x[1], len(x[0]), sorted(x[0])))]

    return {"n_transaksi": n, "min_count": min_count,
            "header": [{"item": i, "count": c, "support": c / n} for i, c in header],
            "tree": to_dict(root), "cpb": cpb, "patterns": patterns}


def _mine(base, suffix, min_count, out):
    """Rekursi FP-Growth pada pattern base (path selalu terurut sesuai header table)."""
    agg = Counter()
    for path, c in base:
        for i in path:
            agg[i] += c
    for item, c in agg.items():
        if c < min_count:
            continue
        new_suffix = (item,) + suffix
        out[frozenset(new_suffix)] = c
        nb = [(p[:p.index(item)], cnt) for p, cnt in base if item in p]
        _mine([(p, cnt) for p, cnt in nb if p], new_suffix, min_count, out)


# ------------------------------------------------------------------ tampilan FP-Tree
def count_nodes(tree: dict) -> int:
    return 1 + sum(count_nodes(c) for c in tree["children"])


def tree_to_dot(tree: dict, branch: str | None = None, direction: str = "LR") -> str:
    """DOT (Graphviz). Node = 'Item\\nCount' seperti Gambar 4.20-4.30 skripsi. branch=None -> seluruh pohon."""
    lines = ["digraph FP {", f'bgcolor="transparent"; rankdir={direction}; nodesep=0.15; ranksep=0.5;',
             'node [shape=ellipse style=filled fillcolor="#DCE6E4" color="#2F5D62" fontname="Helvetica" '
             'fontsize=11 fontcolor="#22373A" penwidth=1.5];',
             'edge [color="#6B7468" arrowhead=none penwidth=1.2];']
    seq = [0]

    def walk(nd, parent_id, label):
        my = f"n{seq[0]}"
        seq[0] += 1
        shape = ' shape=box style="filled,rounded" fillcolor="#22373A" fontcolor="#F1EEE6"' if nd["item"] is None else ""
        lines.append(f'{my} [label="{label}"{shape}];')
        if parent_id:
            lines.append(f"{parent_id} -> {my};")
        for c in nd["children"]:
            walk(c, my, f'{c["item"]}\\n{c["count"]}')

    if branch is None:
        walk(tree, None, "ROOT")
    else:
        sub = next(c for c in tree["children"] if c["item"] == branch)
        walk({"item": None, "count": 0, "children": [sub]}, None, "ROOT")
    lines.append("}")
    return "\n".join(lines)


def tree_to_text(tree: dict) -> str:
    out = ["ROOT"]

    def walk(nd, depth):
        for c in nd["children"]:
            out.append("    " * depth + f"└─ {c['item']} ({c['count']})")
            walk(c, depth + 1)
    walk(tree, 0)
    return "\n".join(out)


# ------------------------------------------------------------------ rekomendasi bisnis
def make_recommendations(rules: list, top: int = 10) -> list:
    """Terjemahkan aturan (lift tertinggi) menjadi saran penataan produk & pengelolaan stok (Bab 4.1.2.2 poin 7)."""
    def join(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " dan " + xs[-1]

    out = []
    for r in sorted(rules, key=lambda r: (-r["lift"], -r["confidence"]))[:top]:
        a, c = r["antecedent"], r["consequent"]
        semua = join(a + c)
        out.append({
            "judul": f"{' + '.join(a)} → {' + '.join(c)}",
            "deskripsi": (f"Jika pelanggan membeli {join(a)}, maka pelanggan cenderung membeli {join(c)} "
                          f"(support {r['support']*100:.2f}%, confidence {r['confidence']*100:.2f}%, lift {r['lift']:.2f}).\n"
                          f"• Produk {semua} dapat ditempatkan pada area rak yang berdekatan.\n"
                          f"• Ketersediaan stok {join(c)} perlu diperhatikan ketika {join(a)} banyak tersedia."),
        })
    return out
