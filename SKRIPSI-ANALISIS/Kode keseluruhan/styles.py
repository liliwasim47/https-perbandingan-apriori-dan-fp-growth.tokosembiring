"""Tema visual: hijau-teal gelap + krem hangat + aksen emas kuningan (elegan, tidak terlalu terang)."""
import streamlit as st

C = {
    "bg": "#E6E2D8", "card": "#F1EEE6", "line": "#CFC8B8", "side": "#22373A", "side2": "#2C4649",
    "teal": "#2F5D62", "teal_d": "#264B4F", "gold": "#B08D57", "text": "#263238", "muted": "#6B7468",
    "apriori": "#2F5D62", "fpg": "#B08D57",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ font-family: 'Inter', sans-serif; color: {C['text']}; }}
.stApp {{ background: {C['bg']}; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.6rem; max-width: 1250px; }}
h1, h2, h3 {{ font-family: 'Playfair Display', serif !important; color: {C['side']}; letter-spacing: .2px; }}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {C['side']} 0%, #1B2D30 100%); border-right: 1px solid #10201f; }}
section[data-testid="stSidebar"] * {{ color: #E9E4D6; }}
.brand {{ font-family:'Playfair Display',serif; font-size:1.28rem; font-weight:700; line-height:1.3;
  padding: .9rem .9rem; margin-bottom:.8rem; border:1px solid {C['gold']}66; border-radius:14px;
  background:{C['side2']}; text-align:center; color:#F1EEE6; }}
.brand small {{ display:block; font-family:'Inter'; font-weight:400; font-size:.72rem; color:{C['gold']}; letter-spacing:2px; margin-top:.25rem; }}
.stApp /* tombol menu: selektor dibuat spesifik agar tidak tertimpa aturan tombol utama */
.stApp section[data-testid="stSidebar"] .stButton > button {{ width:100%; justify-content:flex-start; text-align:left;
  border-radius:12px; padding:.6rem 1rem; font-weight:500; transition: all .15s; }}
.stApp section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
  background:{C['side2']}; border:1px solid #4A6467; color:#F1EEE6; }}
.stApp section[data-testid="stSidebar"] .stButton > button[kind="secondary"] p,
.stApp section[data-testid="stSidebar"] .stButton > button[kind="secondary"] span {{ color:#F1EEE6 !important; font-weight:500; }}
.stApp section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
  background:#3A5A5E; border-color:{C['gold']}; }}
.stApp section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background:linear-gradient(90deg,#C9A76B,{C['gold']}); border:1px solid #D9BC85; box-shadow:0 2px 8px rgba(0,0,0,.25); }}
.stApp section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
.stApp section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {{ color:#1B2D30 !important; font-weight:700; }}
.stApp section[data-testid="stSidebar"] .st-key-logout button[kind] {{ background:#5A3636; border:1px solid #9B6B6B; }}
.stApp section[data-testid="stSidebar"] .st-key-logout button p {{ color:#F6E9E6 !important; font-weight:600; }}
.stApp section[data-testid="stSidebar"] .st-key-logout button[kind]:hover {{ background:#7A4646; }}

/* ---------- tombol utama ---------- */
.stApp .stButton > button, .stApp .stDownloadButton > button {{ border-radius:10px; border:1px solid {C['teal']}; font-weight:600; transition: all .15s; }}
.stApp .stButton > button[kind="primary"], .stApp .stDownloadButton > button {{ background:{C['teal']}; color:#F6F3EC; border-color:{C['teal']}; }}
.stApp .stButton > button[kind="primary"]:hover, .stApp .stDownloadButton > button:hover {{ background:{C['teal_d']}; border-color:{C['teal_d']}; color:#fff; }}
.stApp .stButton > button[kind="secondary"] {{ background:{C['card']}; color:{C['teal']}; }}
.stApp .stButton > button[kind="secondary"]:hover {{ background:#E3DED1; border-color:{C['gold']}; color:{C['side']}; }}
[class*="st-key-danger"] button {{ background:#8A4B45 !important; border-color:#8A4B45 !important; color:#F6F3EC !important; }}

.stApp .stButton > button[kind="primary"] p, .stApp .stDownloadButton > button p {{ color:#F6F3EC !important; }}
.stApp .stButton > button[kind="secondary"] p {{ color:{C['teal']} !important; font-weight:600; }}
[class*="st-key-danger"] button p {{ color:#F6F3EC !important; }}

/* ---------- komponen ---------- */
.topbar {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:.6rem; }}
.page-title {{ font-family:'Playfair Display',serif; font-size:2rem; font-weight:600; color:{C['side']}; margin:0; }}
.badge {{ background:{C['card']}; border:1px solid {C['gold']}; color:{C['side']}; border-radius:999px; padding:.35rem 1.1rem; font-weight:600; font-size:.88rem; }}
.subtle {{ color:{C['muted']}; margin-bottom:1rem; }}
.welcome {{ font-family:'Playfair Display',serif; letter-spacing:.35em; font-size:1.5rem; text-align:center; color:{C['teal']}; margin:1rem 0 1.6rem; }}
.card {{ background:{C['card']}; border:1.5px solid {C['line']}; border-radius:26px; padding:1.25rem 1rem; text-align:center;
  box-shadow: 0 2px 10px rgba(34,55,58,.08); min-height:118px; display:flex; flex-direction:column; justify-content:center; }}
.card .lbl {{ color:{C['muted']}; font-size:.86rem; font-weight:500; }}
.card .val {{ font-family:'Playfair Display',serif; font-size:1.9rem; font-weight:700; color:{C['teal']}; line-height:1.2; }}
.card .val.sm {{ font-size:1.15rem; }}
.card .desc {{ color:{C['muted']}; font-size:.78rem; }}
.card.mini {{ border-radius:16px; min-height:88px; padding:.8rem .6rem; }}
.card.mini .val {{ font-size:1.45rem; }}
.section {{ font-family:'Playfair Display',serif; font-size:1.25rem; color:{C['side']}; margin:1.2rem 0 .4rem; border-bottom:2px solid {C['gold']}55; padding-bottom:.25rem; }}
.success-box {{ background:#D9E4DA; border:1px solid #8FAE96; color:#22402B; border-radius:14px; padding:.8rem 1.1rem; font-weight:600; margin:.8rem 0; }}
.rec {{ background:{C['card']}; border-left:5px solid {C['gold']}; border-radius:12px; padding:.9rem 1.1rem; margin-bottom:.7rem; box-shadow:0 1px 6px rgba(34,55,58,.07); }}
.rec b {{ font-family:'Playfair Display',serif; color:{C['side']}; font-size:1.05rem; }}
.rec p {{ margin:.35rem 0 0; color:{C['text']}; font-size:.92rem; white-space:pre-line; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:22px; border-color:{C['line']}; background:{C['card']}; }}
div[data-testid="stFileUploader"] section {{ background:{C['card']}; border:2px dashed {C['gold']}; border-radius:22px; }}
.login-wrap h1 {{ text-align:center; font-size:2.1rem; margin-bottom:.2rem; }}
.login-sub {{ text-align:center; color:{C['muted']}; margin-bottom:1.4rem; }}
.hdr-row {{ font-weight:600; color:{C['side']}; border-bottom:2px solid {C['gold']}; padding-bottom:.3rem; margin-top:.6rem; }}
.small-note {{ color:{C['muted']}; font-size:.82rem; }}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def card(label, value, desc="", small=False, mini=False):
    cls = "card mini" if mini else "card"
    v = "val sm" if small else "val"
    d = f'<div class="desc">{desc}</div>' if desc else ""
    st.markdown(f'<div class="{cls}"><div class="lbl">{label}</div><div class="{v}">{value}</div>{d}</div>',
                unsafe_allow_html=True)


def plotly_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Playfair Display, serif", size=16, color=C["side"])),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=C["card"], font=dict(family="Inter", color=C["text"]),
        margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.2),
        xaxis=dict(gridcolor=C["line"]), yaxis=dict(gridcolor=C["line"]))
    return fig