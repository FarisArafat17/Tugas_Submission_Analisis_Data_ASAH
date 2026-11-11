import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
SRC_DIR = BASE / "src"

DELAY_ORDER = [
    "Tepat Waktu (≤0 hari)",
    "Terlambat 1–3 hari",
    "Terlambat 4–7 hari",
    "Terlambat >7 hari",
]
MONETARY_ORDER = ["Low (<50 BRL)", "Medium (50–150 BRL)", "High (150–500 BRL)", "VIP (>500 BRL)"]
RECENCY_ORDER = ["Aktif (≤90 hari)", "Hangat (91–180 hari)", "Dingin (181–365 hari)", "Churn (>365 hari)"]

CATEGORY_LABELS = {
    "health_beauty": "Health & Beauty",
    "watches_gifts": "Watches & Gifts",
    "bed_bath_table": "Bed, Bath & Table",
    "sports_leisure": "Sports & Leisure",
    "computers_accessories": "Computers & Accessories",
    "furniture_decor": "Furniture & Decor",
    "housewares": "Housewares",
    "cool_stuff": "Cool Stuff",
    "auto": "Auto",
    "garden_tools": "Garden Tools",
    "toys": "Toys",
    "baby": "Baby",
    "perfumery": "Perfumery",
    "telephony": "Telephony",
    "office_furniture": "Office Furniture",
    "security_and_services": "Security & Services",
    "fashion_childrens_clothes": "Fashion Children's Clothes",
    "cds_dvds_musicals": "CDs, DVDs & Musicals",
    "home_comfort_2": "Home Comfort 2",
    "flowers": "Flowers",
}

st.set_page_config(
    page_title="Olist Data Lab - Dashboard E-Commerce",
    layout="wide",
    initial_sidebar_state="expanded",
)


def svg_icon(name: str, size: int = 18) -> str:
    # Kumpulan ikon SVG dari komponen Icon pada src/App.tsx
    paths = {
        "grid": '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
        "chart": '<path d="M4 19V9"/><path d="M10 19V5"/><path d="M16 19v-7"/><path d="M22 19H2"/>',
        "truck": '<path d="M10 17h4V5H2v12h3"/><path d="M14 9h4l4 4v4h-3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
        "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v6c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 11v6c0 1.66 4.03 3 9 3s9-1.34 9-3v-6"/>',
        "download": '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
        "chevron": '<path d="m9 18 6-6-6-6"/>',
        "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
        "spark": '<path d="m12 3-1.4 3.6L7 8l3.6 1.4L12 13l1.4-3.6L17 8l-3.6-1.4L12 3Z"/><path d="m5 14-.8 2.2L2 17l2.2.8L5 20l.8-2.2L8 17l-2.2-.8L5 14Z"/><path d="m19 14-.6 1.4L17 16l1.4.6L19 18l.6-1.4L21 16l-1.4-.6L19 14Z"/>',
        "package": '<path d="m21 8-9-5-9 5 9 5 9-5Z"/><path d="m3 8 9 5 9-5v9l-9 5-9-5V8Z"/><path d="M12 13v9"/>',
        "star": '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2Z"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "refresh": '<path d="M20 11a8 8 0 1 0-2.34 5.66"/><path d="M20 5v6h-6"/>',
    }
    inner = paths.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{inner}</svg>'
    )


def render_html(raw_html: str):
    # Menghapus indentasi per baris supaya tidak dianggap blok kode oleh Markdown
    cleaned = "\n".join(line.strip() for line in raw_html.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def style_plotly(fig, height: int = 360):
    # Memastikan semua teks pada grafik Plotly berwarna gelap kontras di atas latar putih
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=14, r=24, t=48, b=14),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="DM Sans, sans-serif", color="#1e293b", size=12),
        title=dict(font=dict(family="Manrope, sans-serif", color="#0f172a", size=15)),
        legend=dict(
            font=dict(color="#1e293b", size=12),
            title=dict(font=dict(color="#0f172a", size=12)),
            bgcolor="rgba(255,255,255,0.9)",
        ),
    )
    fig.update_xaxes(
        tickfont=dict(color="#334155", size=11),
        title_font=dict(color="#1e293b", size=12),
        linecolor="#cbd5e1",
        gridcolor="#f1f5f9",
    )
    fig.update_yaxes(
        tickfont=dict(color="#334155", size=11),
        title_font=dict(color="#1e293b", size=12),
        linecolor="#cbd5e1",
        gridcolor="#f1f5f9",
    )
    return fig


@st.cache_data
def load_css() -> str:
    # Seluruh style dari src/index.css sudah ditanam langsung di sini (standalone)
    base_css = '@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700&display=swap");\n\n\n:root {\n  font-family: "DM Sans", sans-serif;\n  color: #172033;\n  background: #f3f6fa;\n  font-synthesis: none;\n}\n\n\n  body {\n    min-width: 320px;\n    min-height: 100vh;\n    background: #f3f6fa;\n  \n  button,\n  select {\n    font: inherit;\n  }\n  button {\n    cursor: pointer;\n  }\n}\n\n* {\n  scrollbar-width: thin;\n  scrollbar-color: #cbd5e1 transparent;\n}\n\n.app-shell {\n  min-height: 100vh;\n  display: flex;\n  background: #f3f6fa;\n}\n.sidebar {\n  width: 244px;\n  height: 100vh;\n  flex: 0 0 244px;\n  position: sticky;\n  top: 0;\n  z-index: 30;\n  display: flex;\n  flex-direction: column;\n  padding: 0 14px 18px;\n  color: #cad4e3;\n  background: #111a2c;\n  border-right: 1px solid rgba(255, 255, 255, 0.04);\n}\n.brand {\n  height: 76px;\n  display: flex;\n  align-items: center;\n  gap: 11px;\n  padding: 0 8px;\n  border-bottom: 1px solid rgba(255, 255, 255, 0.07);\n}\n.brand-mark {\n  width: 35px;\n  height: 35px;\n  display: flex;\n  align-items: flex-end;\n  justify-content: center;\n  gap: 3px;\n  padding-bottom: 8px;\n  border-radius: 9px;\n  background: linear-gradient(145deg, #347ff4, #7557e8);\n  box-shadow: 0 7px 18px rgba(52, 127, 244, 0.28);\n}\n.brand-mark span {\n  width: 4px;\n  border-radius: 4px;\n  background: white;\n}\n.brand-mark span:nth-child(1) {\n  height: 9px;\n  opacity: 0.7;\n}\n.brand-mark span:nth-child(2) {\n  height: 16px;\n}\n.brand-mark span:nth-child(3) {\n  height: 12px;\n  opacity: 0.85;\n}\n.brand strong {\n  display: block;\n  color: white;\n  font: 700 15px/1 "Manrope";\n  letter-spacing: 0.12em;\n}\n.brand small {\n  display: block;\n  margin-top: 4px;\n  font-size: 8px;\n  letter-spacing: 0.2em;\n  color: #7f8ba0;\n}\n.close-sidebar {\n  display: none !important;\n  margin-left: auto;\n}\n.eyebrow {\n  display: block;\n  margin: 23px 10px 9px;\n  color: #647189;\n  font-size: 9px;\n  font-weight: 700;\n  letter-spacing: 0.13em;\n}\n.workspace button {\n  width: 100%;\n  display: flex;\n  align-items: center;\n  gap: 9px;\n  padding: 9px;\n  border: 1px solid rgba(255, 255, 255, 0.07);\n  border-radius: 9px;\n  color: #d9e2ef;\n  background: rgba(255, 255, 255, 0.035);\n  text-align: left;\n}\n.workspace button > span:nth-child(2) {\n  flex: 1;\n  font-size: 12px;\n  font-weight: 600;\n  line-height: 1.3;\n}\n.workspace button small {\n  color: #77849a;\n  font-size: 9px;\n  font-weight: 400;\n}\n.workspace-icon {\n  display: grid;\n  place-items: center;\n  width: 29px;\n  height: 29px;\n  border-radius: 7px;\n  color: #8eb8ff;\n  background: rgba(52, 127, 244, 0.15);\n}\nnav button {\n  width: 100%;\n  display: flex;\n  align-items: center;\n  gap: 12px;\n  margin: 2px 0;\n  padding: 10px 11px;\n  border: 0;\n  border-radius: 8px;\n  color: #8996ab;\n  background: transparent;\n  font-size: 12px;\n  transition: 0.2s;\n}\nnav button:hover {\n  color: white;\n  background: rgba(255, 255, 255, 0.04);\n}\nnav button.active {\n  color: white;\n  background: linear-gradient(90deg, rgba(52, 127, 244, 0.22), rgba(52, 127, 244, 0.08));\n  box-shadow: inset 2px 0 #4285f4;\n}\n.sidebar-insight {\n  margin-top: auto;\n  padding: 14px;\n  border: 1px solid rgba(112, 150, 223, 0.18);\n  border-radius: 11px;\n  background: linear-gradient(145deg, rgba(52, 127, 244, 0.12), rgba(117, 87, 232, 0.08));\n}\n.insight-icon {\n  width: 29px;\n  height: 29px;\n  display: grid;\n  place-items: center;\n  margin-bottom: 10px;\n  border-radius: 8px;\n  color: #b9cfff;\n  background: rgba(85, 123, 230, 0.22);\n}\n.sidebar-insight strong {\n  color: #f1f5fb;\n  font-size: 11px;\n}\n.sidebar-insight p {\n  margin: 5px 0 11px;\n  color: #8290a7;\n  font-size: 9px;\n  line-height: 1.55;\n}\n.sidebar-insight button {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  padding: 0;\n  border: 0;\n  color: #86b3ff;\n  background: none;\n  font-size: 9px;\n  font-weight: 600;\n}\n.profile {\n  display: flex;\n  align-items: center;\n  gap: 9px;\n  margin-top: 13px;\n  padding: 13px 5px 0;\n  border-top: 1px solid rgba(255, 255, 255, 0.07);\n}\n.avatar {\n  width: 30px;\n  height: 30px;\n  display: grid;\n  place-items: center;\n  border-radius: 50%;\n  color: #dbe8ff;\n  background: #304361;\n  font-size: 9px;\n  font-weight: 700;\n}\n.profile div:nth-child(2) {\n  flex: 1;\n}\n.profile strong,\n.profile small {\n  display: block;\n}\n.profile strong {\n  color: #e1e7f0;\n  font-size: 10px;\n}\n.profile small {\n  color: #69778d;\n  font-size: 8px;\n  margin-top: 2px;\n}\n.profile button {\n  border: 0;\n  color: #77849a;\n  background: none;\n}\n\nmain {\n  min-width: 0;\n  flex: 1;\n}\n.topbar {\n  height: 64px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  padding: 0 31px;\n  border-bottom: 1px solid #e2e8f0;\n  background: rgba(255, 255, 255, 0.9);\n  backdrop-filter: blur(12px);\n}\n.breadcrumb {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  font-size: 11px;\n}\n.breadcrumb span {\n  color: #8a96a8;\n}\n.breadcrumb svg {\n  color: #aab4c3;\n}\n.breadcrumb strong {\n  font-weight: 600;\n}\n.header-actions {\n  display: flex;\n  align-items: center;\n  gap: 19px;\n}\n.data-status {\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  font-size: 9px;\n}\n.data-status i {\n  width: 6px;\n  height: 6px;\n  border-radius: 50%;\n  background: #24b3a7;\n  box-shadow: 0 0 0 3px rgba(36, 179, 167, 0.12);\n}\n.data-status span {\n  color: #8b97a8;\n}\n.data-status strong {\n  font-weight: 600;\n}\n.download-button {\n  display: flex;\n  align-items: center;\n  gap: 7px;\n  padding: 8px 13px;\n  border: 0;\n  border-radius: 7px;\n  color: white;\n  background: #2778ee;\n  box-shadow: 0 5px 14px rgba(39, 120, 238, 0.2);\n  font-size: 10px;\n  font-weight: 600;\n}\n.icon-button {\n  display: grid;\n  place-items: center;\n  border: 0;\n  color: inherit;\n  background: transparent;\n}\n.menu-button {\n  display: none;\n}\n.content {\n  max-width: 1460px;\n  margin: 0 auto;\n  padding: 28px 31px 20px;\n}\n.page-intro {\n  display: flex;\n  align-items: flex-end;\n  justify-content: space-between;\n  gap: 30px;\n  margin-bottom: 23px;\n}\n.section-kicker {\n  color: #347ff4;\n  font-size: 8px;\n  font-weight: 700;\n  letter-spacing: 0.16em;\n}\n.page-intro h1 {\n  margin: 6px 0 6px;\n  color: #151e30;\n  font: 700 25px/1.2 "Manrope";\n  letter-spacing: -0.04em;\n}\n.page-intro p {\n  margin: 0;\n  color: #7c8899;\n  font-size: 10px;\n}\n.filters {\n  display: flex;\n  align-items: flex-end;\n  gap: 8px;\n}\n.filters label > span {\n  display: block;\n  margin: 0 0 5px 2px;\n  color: #8994a5;\n  font-size: 7px;\n  font-weight: 700;\n  letter-spacing: 0.1em;\n}\n.filters label > div {\n  height: 36px;\n  display: flex;\n  align-items: center;\n  gap: 7px;\n  padding: 0 10px;\n  border: 1px solid #dce3ec;\n  border-radius: 7px;\n  background: white;\n  box-shadow: 0 2px 5px rgba(30, 50, 80, 0.03);\n}\n.filters svg {\n  color: #75849a;\n}\n.filters select {\n  min-width: 145px;\n  border: 0;\n  outline: none;\n  color: #4f5b6d;\n  background: transparent;\n  font-size: 9px;\n}\n.filters label:nth-child(2) select {\n  min-width: 102px;\n}\n.refresh-button {\n  width: 36px;\n  height: 36px;\n  display: grid;\n  place-items: center;\n  border: 1px solid #dce3ec;\n  border-radius: 7px;\n  color: #64748b;\n  background: white;\n}\n.metrics {\n  display: grid;\n  grid-template-columns: repeat(4, minmax(0, 1fr));\n  gap: 12px;\n  margin-bottom: 13px;\n}\n.metric-card {\n  position: relative;\n  display: grid;\n  grid-template-columns: 37px 1fr;\n  padding: 15px;\n  border: 1px solid #e1e7ef;\n  border-radius: 10px;\n  background: white;\n  box-shadow: 0 3px 12px rgba(27, 45, 74, 0.035);\n  overflow: hidden;\n}\n.metric-card::after {\n  content: "";\n  position: absolute;\n  right: -20px;\n  top: -25px;\n  width: 80px;\n  height: 80px;\n  border-radius: 50%;\n  background: radial-gradient(circle, rgba(52, 127, 244, 0.055), transparent 70%);\n}\n.metric-icon {\n  width: 34px;\n  height: 34px;\n  display: grid;\n  place-items: center;\n  border-radius: 8px;\n}\n.metric-icon.blue {\n  color: #347ff4;\n  background: #eef5ff;\n}\n.metric-icon.purple {\n  color: #7557e8;\n  background: #f2efff;\n}\n.metric-icon.teal {\n  color: #24a99f;\n  background: #eafaf8;\n}\n.metric-icon.orange {\n  color: #e19032;\n  background: #fff6e9;\n}\n.metric-meta span,\n.metric-meta small {\n  display: block;\n}\n.metric-meta span {\n  color: #566276;\n  font-size: 9px;\n  font-weight: 600;\n}\n.metric-meta small {\n  margin-top: 3px;\n  color: #a0a9b7;\n  font-size: 7px;\n}\n.metric-card > strong {\n  grid-column: 1/-1;\n  margin-top: 12px;\n  font: 700 21px/1 "Manrope";\n  letter-spacing: -0.04em;\n}\n.metric-change {\n  grid-column: 1/-1;\n  margin-top: 9px;\n  color: #9aa4b3;\n  font-size: 7px;\n}\n.metric-change span {\n  margin-right: 4px;\n  color: #21a293;\n  font-weight: 700;\n}\n.metric-change.down span {\n  color: #e45c65;\n}\n.analysis-grid {\n  display: grid;\n  grid-template-columns: minmax(0, 1.65fr) minmax(310px, 0.92fr);\n  gap: 13px;\n  margin-bottom: 13px;\n}\n.panel {\n  padding: 18px 19px;\n  border: 1px solid #e1e7ef;\n  border-radius: 10px;\n  background: white;\n  box-shadow: 0 3px 12px rgba(27, 45, 74, 0.035);\n}\n.panel-heading {\n  display: flex;\n  align-items: flex-start;\n  justify-content: space-between;\n  gap: 15px;\n}\n.panel-heading h2 {\n  margin: 5px 0 0;\n  font: 700 13px/1.3 "Manrope";\n  letter-spacing: -0.02em;\n}\n.panel-heading button {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  padding: 3px;\n  border: 0;\n  color: #347ff4;\n  background: none;\n  font-size: 8px;\n  font-weight: 600;\n}\n.panel-stat {\n  text-align: right;\n}\n.panel-stat span,\n.panel-stat strong {\n  display: block;\n}\n.panel-stat span {\n  color: #9aa5b5;\n  font-size: 7px;\n}\n.panel-stat strong {\n  margin-top: 4px;\n  font: 700 12px "Manrope";\n}\n.trend-chart {\n  height: 205px;\n  display: flex;\n  margin-top: 20px;\n}\n.y-labels {\n  width: 32px;\n  display: flex;\n  flex-direction: column;\n  justify-content: space-between;\n  padding: 0 0 21px;\n  color: #a3adba;\n  font-size: 7px;\n}\n.trend-plot {\n  position: relative;\n  flex: 1;\n}\n.grid-lines {\n  position: absolute;\n  inset: 0 0 21px;\n  display: flex;\n  flex-direction: column;\n  justify-content: space-between;\n}\n.grid-lines i {\n  height: 1px;\n  background: #edf1f6;\n}\n.trend-plot svg {\n  position: absolute;\n  inset: 0 0 21px;\n  width: 100%;\n  height: calc(100% - 21px);\n  overflow: visible;\n}\n.x-labels {\n  position: absolute;\n  bottom: 0;\n  left: 0;\n  right: 0;\n  display: flex;\n  justify-content: space-between;\n  color: #9ba6b5;\n  font-size: 7px;\n}\n.chart-note {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  margin: 3px 0 0 32px;\n  padding-top: 11px;\n  border-top: 1px solid #edf1f6;\n  color: #738096;\n  font-size: 7px;\n}\n.chart-note span {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n}\n.chart-note i {\n  width: 7px;\n  height: 2px;\n  background: #347ff4;\n}\n.chart-note small {\n  color: #a0a9b7;\n  font-size: 7px;\n}\n.bar-list {\n  display: flex;\n  flex-direction: column;\n  gap: 13px;\n  margin-top: 22px;\n}\n.bar-row {\n  display: grid;\n  grid-template-columns: 86px 1fr 36px 31px;\n  align-items: center;\n  gap: 7px;\n}\n.bar-row > span {\n  color: #68758a;\n  font-size: 8px;\n  white-space: nowrap;\n  overflow: hidden;\n  text-overflow: ellipsis;\n}\n.bar-track {\n  height: 6px;\n  border-radius: 5px;\n  background: #edf2f7;\n  overflow: hidden;\n}\n.bar-track i {\n  display: block;\n  height: 100%;\n  border-radius: 5px;\n  background: linear-gradient(90deg, #347ff4, #5a91f1);\n}\n.bar-row strong {\n  font-size: 8px;\n  text-align: right;\n}\n.bar-row small {\n  color: #9aa5b5;\n  font-size: 7px;\n  text-align: right;\n}\n.highlight-box {\n  display: flex;\n  align-items: center;\n  gap: 9px;\n  margin-top: 19px;\n  padding: 9px 10px;\n  border: 1px solid #dce9ff;\n  border-radius: 7px;\n  background: #f6f9ff;\n}\n.highlight-box div {\n  width: 25px;\n  height: 25px;\n  display: grid;\n  place-items: center;\n  border-radius: 6px;\n  color: #347ff4;\n  background: #e7f0ff;\n}\n.highlight-box p {\n  margin: 0;\n  color: #6c788b;\n  font-size: 8px;\n}\n.highlight-box strong {\n  color: #347ff4;\n}\n.lower-grid {\n  display: grid;\n  grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.74fr);\n  gap: 13px;\n}\n.delivery-content {\n  display: grid;\n  grid-template-columns: 1fr 170px;\n  gap: 24px;\n  margin-top: 18px;\n}\n.delivery-bars {\n  height: 135px;\n  display: flex;\n  justify-content: space-around;\n  gap: 14px;\n  padding: 0 10px;\n  border-bottom: 1px solid #e7ecf2;\n}\n.delivery-item {\n  flex: 1;\n  display: grid;\n  grid-template-rows: 15px 1fr 23px;\n  justify-items: center;\n  max-width: 58px;\n}\n.delivery-item strong {\n  font-size: 8px;\n}\n.vertical-track {\n  position: relative;\n  width: 21px;\n  height: 100%;\n  background: #f1f4f8;\n  border-radius: 4px 4px 0 0;\n  overflow: hidden;\n}\n.vertical-track i {\n  position: absolute;\n  bottom: 0;\n  left: 0;\n  width: 100%;\n  border-radius: 4px 4px 0 0;\n}\n.delivery-item span {\n  margin-top: 7px;\n  color: #8290a2;\n  font-size: 7px;\n  white-space: nowrap;\n}\n.delivery-insight {\n  padding: 12px 14px;\n  border-radius: 8px;\n  background: #f7f9fc;\n}\n.delivery-insight > span {\n  color: #e45c65;\n  font-size: 7px;\n  font-weight: 700;\n  letter-spacing: 0.1em;\n}\n.delivery-insight > strong {\n  display: block;\n  margin: 8px 0 4px;\n  color: #d94855;\n  font: 700 20px "Manrope";\n}\n.delivery-insight p {\n  margin: 0;\n  color: #778498;\n  font-size: 8px;\n  line-height: 1.5;\n}\n.delivery-insight div {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  margin-top: 12px;\n  color: #8c97a7;\n}\n.delivery-insight i {\n  width: 6px;\n  height: 6px;\n  border-radius: 50%;\n  background: #e45c65;\n}\n.delivery-insight small {\n  font-size: 7px;\n}\n.recommendation {\n  padding: 18px 20px;\n  border-radius: 10px;\n  color: white;\n  background: linear-gradient(140deg, #192f57, #1f4780);\n  box-shadow: 0 6px 18px rgba(24, 52, 93, 0.15);\n  overflow: hidden;\n  position: relative;\n}\n.recommendation::after {\n  content: "";\n  position: absolute;\n  width: 190px;\n  height: 190px;\n  right: -95px;\n  bottom: -105px;\n  border: 1px solid rgba(255, 255, 255, 0.1);\n  border-radius: 50%;\n  box-shadow:\n    0 0 0 25px rgba(255, 255, 255, 0.025),\n    0 0 0 52px rgba(255, 255, 255, 0.018);\n}\n.recommendation-top {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n}\n.recommendation-top span {\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  color: #a8c8ff;\n  font-size: 7px;\n  font-weight: 700;\n  letter-spacing: 0.1em;\n}\n.recommendation-top small {\n  padding: 4px 6px;\n  border-radius: 4px;\n  color: #ffcf93;\n  background: rgba(244, 166, 65, 0.16);\n  font-size: 6px;\n  font-weight: 700;\n}\n.recommendation h2 {\n  position: relative;\n  z-index: 1;\n  margin: 20px 0 8px;\n  max-width: 260px;\n  font: 700 16px/1.35 "Manrope";\n}\n.recommendation p {\n  position: relative;\n  z-index: 1;\n  margin: 0;\n  max-width: 310px;\n  color: #b3c2d8;\n  font-size: 8px;\n  line-height: 1.6;\n}\n.recommendation button {\n  position: relative;\n  z-index: 1;\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  margin-top: 16px;\n  padding: 0;\n  border: 0;\n  color: #8eb8ff;\n  background: none;\n  font-size: 8px;\n  font-weight: 600;\n}\n.rfm-grid {\n  margin-top: 0;\n}\n.pill {\n  padding: 5px 8px;\n  border-radius: 10px;\n  color: #7557e8;\n  background: #f2efff;\n  font-size: 7px;\n  font-weight: 600;\n}\n.donut-wrap {\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  gap: 45px;\n  margin-top: 30px;\n}\n.donut {\n  width: 150px;\n  height: 150px;\n  display: grid;\n  place-items: center;\n  border-radius: 50%;\n  background: conic-gradient(\n    #347ff4 0 4.8%,\n    #7557e8 4.8% 23.4%,\n    #25b2a8 23.4% 65.7%,\n    #cbd5e1 65.7%\n  );\n}\n.donut::before {\n  content: "";\n  position: absolute;\n  width: 92px;\n  height: 92px;\n  border-radius: 50%;\n  background: white;\n}\n.donut div {\n  position: relative;\n  z-index: 1;\n  text-align: center;\n}\n.donut strong,\n.donut span {\n  display: block;\n}\n.donut strong {\n  font: 700 17px "Manrope";\n}\n.donut span {\n  color: #98a3b3;\n  font-size: 7px;\n}\n.legend {\n  min-width: 165px;\n}\n.legend > div {\n  display: grid;\n  grid-template-columns: 8px 1fr auto;\n  align-items: center;\n  gap: 8px;\n  margin: 12px 0;\n  font-size: 8px;\n}\n.legend i {\n  width: 7px;\n  height: 7px;\n  border-radius: 2px;\n}\n.legend span {\n  color: #707d91;\n}\n.recency-list {\n  margin-top: 28px;\n}\n.recency-list > div {\n  display: grid;\n  grid-template-columns: 1fr auto;\n  gap: 8px;\n  margin: 17px 0;\n}\n.recency-list span,\n.recency-list strong {\n  font-size: 8px;\n}\n.recency-list span {\n  color: #69768a;\n}\n.recency-list > div > div {\n  grid-column: 1/-1;\n  height: 7px;\n  border-radius: 5px;\n  background: #eef2f6;\n  overflow: hidden;\n}\n.recency-list i {\n  display: block;\n  height: 100%;\n  border-radius: 5px;\n}\nfooter {\n  display: flex;\n  justify-content: space-between;\n  margin-top: 18px;\n  padding: 0 3px;\n  color: #9ba5b4;\n  font-size: 7px;\n}\n.toast {\n  position: fixed;\n  right: 24px;\n  bottom: 24px;\n  z-index: 60;\n  padding: 11px 16px;\n  border-radius: 8px;\n  color: white;\n  background: #18243a;\n  box-shadow: 0 10px 30px rgba(10, 20, 40, 0.2);\n  font-size: 10px;\n}\n.backdrop {\n  display: none;\n}\n\n@media (max-width: 1050px) {\n  .sidebar {\n    width: 215px;\n    flex-basis: 215px;\n  }\n  .metrics {\n    grid-template-columns: repeat(2, 1fr);\n  }\n  .analysis-grid,\n  .lower-grid {\n    grid-template-columns: 1fr;\n  }\n  .category-panel {\n    min-height: 300px;\n  }\n  .filters {\n    flex-wrap: wrap;\n    justify-content: flex-end;\n  }\n  .page-intro {\n    align-items: flex-start;\n  }\n  .delivery-content {\n    grid-template-columns: 1fr 190px;\n  }\n}\n@media (max-width: 760px) {\n  .sidebar {\n    position: fixed;\n    left: 0;\n    transform: translateX(-105%);\n    width: 244px;\n    transition: transform 0.25s ease;\n    box-shadow: 15px 0 40px rgba(10, 20, 40, 0.25);\n  }\n  .sidebar-open {\n    transform: translateX(0);\n  }\n  .close-sidebar,\n  .menu-button {\n    display: grid !important;\n  }\n  .backdrop {\n    display: block;\n    position: fixed;\n    inset: 0;\n    z-index: 20;\n    border: 0;\n    background: rgba(10, 18, 32, 0.48);\n  }\n  .topbar {\n    height: 58px;\n    padding: 0 18px;\n  }\n  .breadcrumb {\n    margin-right: auto;\n    margin-left: 13px;\n  }\n  .data-status {\n    display: none;\n  }\n  .content {\n    padding: 22px 18px;\n  }\n  .page-intro {\n    display: block;\n  }\n  .filters {\n    justify-content: flex-start;\n    margin-top: 20px;\n  }\n  .metrics {\n    grid-template-columns: repeat(2, 1fr);\n  }\n  .analysis-grid,\n  .lower-grid {\n    grid-template-columns: 1fr;\n  }\n  .trend-panel {\n    overflow: hidden;\n  }\n  .download-button span {\n    display: none;\n  }\n  .download-button {\n    padding: 9px;\n  }\n  .delivery-content {\n    grid-template-columns: 1fr;\n  }\n  .delivery-insight {\n    margin-top: 5px;\n  }\n  .donut-wrap {\n    gap: 25px;\n  }\n  .page-intro h1 {\n    font-size: 22px;\n  }\n}\n@media (max-width: 500px) {\n  .metrics {\n    grid-template-columns: 1fr;\n  }\n  .filters label:first-child {\n    width: 100%;\n  }\n  .filters label:first-child > div,\n  .filters label:first-child select {\n    width: 100%;\n  }\n  .analysis-grid {\n    display: block;\n  }\n  .panel {\n    margin-bottom: 12px;\n  }\n  .bar-row {\n    grid-template-columns: 75px 1fr 32px;\n  }\n  .bar-row small {\n    display: none;\n  }\n  .chart-note small {\n    display: none;\n  }\n  .delivery-bars {\n    padding: 0;\n    gap: 5px;\n  }\n  .donut-wrap {\n    flex-direction: column;\n  }\n  .legend {\n    width: 100%;\n  }\n  .topbar {\n    padding: 0 14px;\n  }\n  .content {\n    padding: 20px 14px;\n  }\n  .breadcrumb span,\n  .breadcrumb svg {\n    display: none;\n  }\n  footer {\n    display: block;\n  }\n  footer span {\n    display: block;\n    margin-top: 5px;\n  }\n}\n'

    # Penyesuaian warna huruf kontras tinggi agar tidak ada teks putih di atas latar putih/terang
    streamlit_bridge_css = """
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
    }
    .stApp {
        background: #f3f6fa !important;
        font-family: "DM Sans", sans-serif !important;
        color: #0f172a !important;
    }
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1500px !important;
        color: #0f172a !important;
    }

    /* ---------------- Sidebar Gelap (Teks Terang Kontras) ---------------- */
    section[data-testid="stSidebar"] {
        background: #111a2c !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        width: 262px !important;
    }
    section[data-testid="stSidebar"] > div {
        background: #111a2c !important;
        padding-top: 0.5rem !important;
    }
    section[data-testid="stSidebar"] .brand strong {
        color: #ffffff !important;
        font-size: 16px !important;
    }
    section[data-testid="stSidebar"] .brand small {
        color: #94a3b8 !important;
        font-size: 9px !important;
    }
    section[data-testid="stSidebar"] .eyebrow {
        color: #94a3b8 !important;
        font-size: 10px !important;
    }
    section[data-testid="stSidebar"] .workspace button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .workspace button span {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .workspace button small {
        color: #94a3b8 !important;
        font-size: 10.5px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        justify-content: flex-start;
        text-align: left;
        padding: 10px 12px;
        border: 0 !important;
        border-radius: 8px;
        color: #cbd5e1 !important;
        background: transparent !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        transition: 0.2s;
        margin: 2px 0;
    }
    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stButton > button span {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover p,
    section[data-testid="stSidebar"] div.stButton > button:hover span {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        color: #ffffff !important;
        background: linear-gradient(90deg, rgba(52, 127, 244, 0.28), rgba(52, 127, 244, 0.1)) !important;
        box-shadow: inset 3px 0 #4285f4 !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] .sidebar-insight strong {
        color: #ffffff !important;
        font-size: 13px !important;
    }
    section[data-testid="stSidebar"] .sidebar-insight p {
        color: #cbd5e1 !important;
        font-size: 11.5px !important;
    }
    section[data-testid="stSidebar"] .profile strong {
        color: #f8fafc !important;
        font-size: 12.5px !important;
    }
    section[data-testid="stSidebar"] .profile small {
        color: #94a3b8 !important;
        font-size: 11px !important;
    }

    /* ---------------- Filter Selectbox & Tombol Unduh di Area Utama ---------------- */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stSelectbox"] label span {
        color: #334155 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04) !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #334155 !important;
        color: #334155 !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: 0 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 5px 14px rgba(37, 99, 235, 0.22) !important;
        width: 100%;
    }
    div[data-testid="stDownloadButton"] > button p,
    div[data-testid="stDownloadButton"] > button span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ---------------- Topbar & Judul Halaman (Teks Gelap Kontras di Atas Putih) ---------------- */
    .topbar {
        margin: 0 -2rem 22px -2rem;
        padding: 0 32px;
        height: 62px;
        border-radius: 0;
        background: #ffffff !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    .breadcrumb { font-size: 13.5px !important; }
    .breadcrumb span { color: #475569 !important; font-weight: 500 !important; }
    .breadcrumb svg { color: #64748b !important; }
    .breadcrumb strong { color: #0f172a !important; font-weight: 700 !important; }
    .data-status { font-size: 12.5px !important; }
    .data-status span { color: #475569 !important; font-weight: 500 !important; }
    .data-status strong { color: #0f172a !important; font-weight: 700 !important; }

    .section-kicker {
        color: #2563eb !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
    }
    .page-intro h1 {
        color: #0f172a !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 6px 0 !important;
    }
    .page-intro p {
        color: #475569 !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }

    /* ---------------- Metric Cards (Latar Putih, Teks Gelap Jelas) ---------------- */
    .metric-card {
        padding: 18px !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        border: 1px solid #dbe3ee !important;
    }
    .metric-meta span {
        color: #1e293b !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
    }
    .metric-meta small {
        color: #475569 !important;
        font-size: 11.5px !important;
        font-weight: 500 !important;
    }
    .metric-card > strong {
        color: #0f172a !important;
        font-size: 27px !important;
        font-weight: 800 !important;
        margin-top: 14px !important;
    }
    .metric-change {
        color: #475569 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        margin-top: 10px !important;
    }
    .metric-change span {
        color: #0d9488 !important;
        font-weight: 700 !important;
    }
    .metric-change.down span {
        color: #dc2626 !important;
        font-weight: 700 !important;
    }

    /* ---------------- Panel Analisis (Latar Putih, Teks Gelap Kontras) ---------------- */
    .panel {
        padding: 20px 22px !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        border: 1px solid #dbe3ee !important;
        color: #0f172a !important;
    }
    .panel-heading h2 {
        color: #0f172a !important;
        font-size: 17px !important;
        font-weight: 700 !important;
    }
    .panel-stat span {
        color: #475569 !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
    }
    .panel-stat strong {
        color: #0f172a !important;
        font-size: 15.5px !important;
        font-weight: 800 !important;
    }
    .y-labels {
        width: 44px !important;
        color: #334155 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    .y-labels span { color: #334155 !important; }
    .x-labels {
        color: #334155 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    .x-labels span { color: #334155 !important; }
    .chart-note {
        font-size: 12px !important;
        margin-left: 44px !important;
        color: #334155 !important;
        font-weight: 500 !important;
    }
    .chart-note span { color: #1e293b !important; font-weight: 600 !important; }
    .chart-note small { color: #475569 !important; font-size: 11.5px !important; font-weight: 500 !important; }

    /* Baris Kategori & Negara Bagian */
    .bar-row {
        grid-template-columns: 145px 1fr 64px 52px !important;
        gap: 10px !important;
    }
    .bar-row > span {
        color: #1e293b !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .bar-row > span strong {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    .bar-row > strong {
        color: #0f172a !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    .bar-row > small {
        color: #334155 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }
    .bar-track { height: 8px !important; background: #e2e8f0 !important; }

    .highlight-box {
        background: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
    }
    .highlight-box p {
        color: #1e293b !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .highlight-box strong {
        color: #1d4ed8 !important;
        font-weight: 700 !important;
    }

    /* Grafik Batang Pengiriman & Kotak Insight */
    .delivery-content { grid-template-columns: 1fr 225px !important; gap: 24px !important; }
    .delivery-bars { height: 155px !important; border-bottom: 1px solid #cbd5e1 !important; }
    .delivery-item { max-width: 82px !important; grid-template-rows: 22px 1fr 28px !important; }
    .delivery-item strong {
        color: #0f172a !important;
        font-size: 13px !important;
        font-weight: 800 !important;
    }
    .delivery-item span {
        color: #1e293b !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
    }
    .vertical-track { width: 28px !important; background: #e2e8f0 !important; }

    .delivery-insight {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
    }
    .delivery-insight > span {
        color: #dc2626 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
    }
    .delivery-insight > strong {
        color: #b91c1c !important;
        font-size: 24px !important;
        font-weight: 800 !important;
    }
    .delivery-insight p {
        color: #1e293b !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
    }
    .delivery-insight small {
        color: #334155 !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
    }

    /* Kartu Rekomendasi (Latar Biru Tua Gelap, Teks Terang Kontras) */
    .recommendation {
        padding: 22px 24px !important;
        border-radius: 12px !important;
        background: linear-gradient(140deg, #192f57, #1f4780) !important;
        color: #ffffff !important;
    }
    .recommendation-top span {
        color: #bfdbfe !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
    }
    .recommendation-top small {
        color: #fde68a !important;
        background: rgba(245, 158, 11, 0.22) !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
        padding: 4px 8px !important;
    }
    .recommendation h2 {
        color: #ffffff !important;
        font-size: 19px !important;
        font-weight: 700 !important;
        max-width: 100% !important;
        margin: 16px 0 8px !important;
    }
    .recommendation p {
        color: #e2e8f0 !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        max-width: 100% !important;
    }

    /* Panel RFM Donut & Recency */
    .pill {
        font-size: 11.5px !important;
        font-weight: 700 !important;
        padding: 5px 10px !important;
        color: #5b21b6 !important;
        background: #ede9fe !important;
    }
    .donut { width: 170px !important; height: 170px !important; position: relative !important; }
    .donut::before { width: 106px !important; height: 106px !important; background: #ffffff !important; }
    .donut strong {
        color: #0f172a !important;
        font-size: 20px !important;
        font-weight: 800 !important;
    }
    .donut span {
        color: #334155 !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
    }
    .legend { min-width: 220px !important; }
    .legend > div { font-size: 13px !important; margin: 13px 0 !important; }
    .legend span { color: #1e293b !important; font-weight: 500 !important; }
    .legend strong { color: #0f172a !important; font-weight: 700 !important; }

    .recency-list > div { margin: 18px 0 !important; }
    .recency-list span {
        color: #1e293b !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .recency-list strong {
        color: #0f172a !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    .recency-list > div > div { height: 8px !important; background: #e2e8f0 !important; }

    footer {
        font-size: 12.5px !important;
        margin-top: 24px !important;
        padding-top: 14px !important;
        border-top: 1px solid #cbd5e1 !important;
        color: #334155 !important;
        font-weight: 500 !important;
    }
    footer span { color: #334155 !important; font-weight: 500 !important; }
    """
    return f"<style>{base_css}\n{streamlit_bridge_css}</style>"


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(BASE / "main_data.csv", parse_dates=["order_purchase_date"])


def pretty_category(cat_key: str) -> str:
    if cat_key in CATEGORY_LABELS:
        return CATEGORY_LABELS[cat_key]
    return str(cat_key).replace("_", " ").title()


def build_trend_svg(monthly_df: pd.DataFrame) -> str:
    if monthly_df.empty:
        return "<p>Tidak ada data tren bulanan.</p>"

    if len(monthly_df) > 12:
        idx = np.linspace(0, len(monthly_df) - 1, 12).round().astype(int)
        sampled = monthly_df.iloc[idx].reset_index(drop=True)
    else:
        sampled = monthly_df.reset_index(drop=True)

    max_rev = max(float(sampled["revenue"].max()), 1.0)
    n_pts = len(sampled)

    scaled_vals = [12 + (val / max_rev) * 58 for val in sampled["revenue"]]
    coords = [
        f"{(i / max(n_pts - 1, 1)) * 100:.2f},{78 - v:.2f}"
        for i, v in enumerate(scaled_vals)
    ]
    points_str = " ".join(coords)

    circles_html = "".join(
        f'<circle cx="{(i / max(n_pts - 1, 1)) * 100:.2f}" cy="{78 - v:.2f}" '
        f'r="1.2" fill="#fff" stroke="#347ff4" stroke-width=".7" />'
        for i, v in enumerate(scaled_vals)
    )

    month_names_id = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "Mei", "06": "Jun", "07": "Jul", "08": "Agu",
        "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des",
    }
    x_labels_html = "".join(
        f"<span>{month_names_id.get(m.split('-')[1], m)} '{m[2:4]}</span>"
        for m in sampled["month"]
    )

    y_steps = [max_rev * r for r in (1.0, 0.75, 0.5, 0.25, 0.0)]
    y_labels_html = "".join(
        f"<span>{v / 1e6:.1f}M</span>" if v >= 1e6 else (f"<span>{v / 1e3:.0f}K</span>" if v > 0 else "<span>0</span>")
        for v in y_steps
    )

    return f"""
    <div class="trend-chart">
      <div class="y-labels">{y_labels_html}</div>
      <div class="trend-plot">
        <div class="grid-lines"><i></i><i></i><i></i><i></i><i></i></div>
        <svg viewBox="0 0 100 80" preserveAspectRatio="none" role="img" aria-label="Grafik tren pendapatan bulanan">
          <defs>
            <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#2b7fff" stop-opacity=".28" />
              <stop offset="1" stop-color="#2b7fff" stop-opacity="0" />
            </linearGradient>
          </defs>
          <polygon points="0,80 {points_str} 100,80" fill="url(#area)" />
          <polyline points="{points_str}" fill="none" stroke="#347ff4" stroke-width="1.8" vector-effect="non-scaling-stroke" />
          {circles_html}
        </svg>
        <div class="x-labels">{x_labels_html}</div>
      </div>
    </div>
    """


def build_category_bars_html(cat_rows: pd.DataFrame, max_val: float, bar_color: str = "linear-gradient(90deg, #347ff4, #5a91f1)") -> str:
    rows_html = []
    for _, row in cat_rows.iterrows():
        width_pct = max(4.0, (float(row["revenue"]) / max(max_val, 1.0)) * 100.0)
        rev_val = float(row["revenue"])
        rev_str = f"{rev_val / 1e3:,.0f}K" if rev_val >= 1000 else f"{rev_val:,.0f}"
        rows_html.append(
            f'<div class="bar-row">'
            f'<span title="{pretty_category(row["category"])}">{pretty_category(row["category"])}</span>'
            f'<div class="bar-track"><i style="width:{width_pct:.1f}%;background:{bar_color};"></i></div>'
            f'<strong>{rev_str}</strong>'
            f'<small>{row["share_pct"]:.2f}%</small>'
            f'</div>'
        )
    return f'<div class="bar-list">{"".join(rows_html)}</div>'


def build_delivery_bars_html(dg_df: pd.DataFrame) -> str:
    short_labels = {
        "Tepat Waktu (≤0 hari)": ("Tepat waktu", "#24b3a7"),
        "Terlambat 1–3 hari": ("1–3 hari", "#64748b"),
        "Terlambat 4–7 hari": ("4–7 hari", "#f4a641"),
        "Terlambat >7 hari": (">7 hari", "#e45c65"),
    }
    items_html = []
    for group_key in DELAY_ORDER:
        sub = dg_df[dg_df["delay_group"] == group_key]
        score = float(sub["avg_score"].iloc[0]) if not sub.empty and pd.notna(sub["avg_score"].iloc[0]) else 0.0
        lbl, color = short_labels[group_key]
        height_pct = max(4.0, (score / 5.0) * 100.0) if score > 0 else 0.0
        items_html.append(
            f'<div class="delivery-item">'
            f'<strong>{score:.2f}</strong>'
            f'<div class="vertical-track"><i style="height:{height_pct:.1f}%;background:{color};"></i></div>'
            f'<span>{lbl}</span>'
            f'</div>'
        )
    return f'<div class="delivery-bars">{"".join(items_html)}</div>'


st.markdown(load_css(), unsafe_allow_html=True)
raw_df = load_data()

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Overview"

# ---------------- Sidebar ----------------
with st.sidebar:
    render_html(
        f"""
        <div class="brand">
          <div class="brand-mark"><span></span><span></span><span></span></div>
          <div>
            <strong>OLIST</strong>
            <small>DATA LAB</small>
          </div>
        </div>
        <div class="workspace">
          <span class="eyebrow">WORKSPACE</span>
          <button type="button">
            <span class="workspace-icon">{svg_icon("database", 16)}</span>
            <span>Olist Commerce<br/><small>Public dataset</small></span>
            {svg_icon("chevron", 15)}
          </button>
        </div>
        <span class="eyebrow">ANALISIS</span>
        """
    )

    for nav_label in ["Overview", "Analisis Kategori", "Pengiriman", "Segmentasi RFM"]:
        is_active = st.session_state.active_nav == nav_label
        if st.button(
            nav_label,
            key=f"nav_{nav_label}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_nav = nav_label
            st.rerun()

    render_html(
        f"""
        <div class="sidebar-insight" style="margin-top: 22px;">
          <div class="insight-icon">{svg_icon("spark", 18)}</div>
          <strong>Insight siap</strong>
          <p>3 rekomendasi tindakan tersedia dari hasil analisis transaksi dan pengiriman.</p>
        </div>
        <div class="profile">
          <div class="avatar">FA</div>
          <div>
            <strong>Faris Arafat</strong>
            <small>Data Analyst</small>
          </div>
        </div>
        """
    )

active = st.session_state.active_nav

# ---------------- Topbar ----------------
render_html(
    f"""
    <header class="topbar">
      <div class="breadcrumb">
        <span>Olist Commerce</span>
        {svg_icon("chevron", 13)}
        <strong>{active}</strong>
      </div>
      <div class="header-actions">
        <div class="data-status">
          <i></i>
          <span>Dataset Aktif</span>
          <strong>Sep 2016 – Agu 2018</strong>
        </div>
      </div>
    </header>
    """
)

# ---------------- Page Intro & Filter Bar ----------------
intro_col, filter_col1, filter_col2, filter_col3 = st.columns([1.9, 1.05, 0.9, 0.75])

with intro_col:
    page_title = "Kinerja E-Commerce" if active == "Overview" else active
    render_html(
        f"""
        <div class="page-intro" style="margin-bottom: 10px;">
          <div>
            <span class="section-kicker">DASHBOARD ANALITIK</span>
            <h1>{page_title}</h1>
            <p>Ringkasan performa bisnis dan perilaku pelanggan berdasarkan Brazilian E-Commerce Public Dataset.</p>
          </div>
        </div>
        """
    )

with filter_col1:
    period_choice = st.selectbox(
        "PERIODE",
        options=[
            "Sep 2016 – Agu 2018",
            "Sep 2017 – Agu 2018",
            "Jan 2018 – Agu 2018",
            "Tahun 2017 Penuh",
        ],
        index=0,
    )

with filter_col2:
    delivery_choice = st.selectbox(
        "PENGIRIMAN",
        options=["Semua status", "Tepat Waktu", "Terlambat"],
        index=0,
    )

period_bounds = {
    "Sep 2016 – Agu 2018": ("2016-09-01", "2018-08-31"),
    "Sep 2017 – Agu 2018": ("2017-09-01", "2018-08-31"),
    "Jan 2018 – Agu 2018": ("2018-01-01", "2018-08-31"),
    "Tahun 2017 Penuh": ("2017-01-01", "2017-12-31"),
}
start_str, end_str = period_bounds[period_choice]
mask = raw_df["order_purchase_date"].between(pd.Timestamp(start_str), pd.Timestamp(end_str))
if delivery_choice != "Semua status":
    mask = mask & (raw_df["delivery_status"] == delivery_choice)

items_df = raw_df[mask].copy()
if items_df.empty:
    st.warning("Tidak ada data transaksi untuk kombinasi filter yang dipilih.")
    st.stop()

order_rev_s = items_df.groupby("order_id")["price"].sum().rename("order_revenue")
orders_df = items_df.drop_duplicates("order_id").merge(order_rev_s, on="order_id", how="left")

total_orders = len(orders_df)
total_revenue = float(items_df["price"].sum())
avg_review = float(orders_df["review_score"].mean())
late_orders_cnt = int((orders_df["delivery_status"] == "Terlambat").sum())
late_pct_val = (late_orders_cnt / max(total_orders, 1)) * 100.0

with filter_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    report_csv = (
        "metric,value\n"
        f"Periode,{period_choice}\n"
        f"Status Pengiriman,{delivery_choice}\n"
        f"Total Pesanan,{total_orders}\n"
        f"Pendapatan Produk (BRL),{total_revenue:.2f}\n"
        f"Rata-rata Skor Ulasan,{avg_review:.2f}\n"
        f"Pesanan Terlambat (%),{late_pct_val:.2f}%\n"
    )
    st.download_button(
        label="Unduh laporan",
        data=report_csv,
        file_name="olist-dashboard-summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ---------------- Empat Kartu Metrik Utama ----------------
rev_display = f"{total_revenue / 1e6:.2f}M" if total_revenue >= 1e6 else f"{total_revenue / 1e3:,.1f}K"
score_change_str = "-47.1%" if delivery_choice == "Terlambat" else "+4.29 tepat waktu"
score_down_cls = "down" if delivery_choice == "Terlambat" else ""
score_arrow = "↓" if delivery_choice == "Terlambat" else "↑"

render_html(
    f"""
    <section class="metrics">
      <article class="metric-card">
        <div class="metric-icon blue">{svg_icon("package", 20)}</div>
        <div class="metric-meta">
          <span>Total Pesanan</span>
          <small>Pesanan terkirim</small>
        </div>
        <strong>{total_orders:,}</strong>
        <div class="metric-change">
          <span>↑ {orders_df['customer_unique_id'].nunique():,}</span> pelanggan unik
        </div>
      </article>
      <article class="metric-card">
        <div class="metric-icon purple">{svg_icon("chart", 20)}</div>
        <div class="metric-meta">
          <span>Pendapatan Produk</span>
          <small>Dalam BRL</small>
        </div>
        <strong>{rev_display}</strong>
        <div class="metric-change">
          <span>↑ {len(items_df):,}</span> unit produk terjual
        </div>
      </article>
      <article class="metric-card">
        <div class="metric-icon teal">{svg_icon("star", 20)}</div>
        <div class="metric-meta">
          <span>Skor Ulasan</span>
          <small>Dari 5.00</small>
        </div>
        <strong>{avg_review:.2f}</strong>
        <div class="metric-change {score_down_cls}">
          <span>{score_arrow} {score_change_str.replace('-', '')}</span> rata-rata ulasan
        </div>
      </article>
      <article class="metric-card">
        <div class="metric-icon orange">{svg_icon("clock", 20)}</div>
        <div class="metric-meta">
          <span>Pesanan Terlambat</span>
          <small>{late_orders_cnt:,} pesanan</small>
        </div>
        <strong>{late_pct_val:.2f}%</strong>
        <div class="metric-change {'down' if late_pct_val > 10 else ''}">
          <span>{'↓' if late_pct_val > 10 else '↑'} {orders_df['delivery_days'].mean():.1f} hari</span> rata-rata kirim
        </div>
      </article>
    </section>
    """
)

# Persiapan agregasi untuk seluruh panel
cat_df = (
    items_df[items_df["category"] != "unknown"]
    .groupby("category", as_index=False)
    .agg(revenue=("price", "sum"), items_sold=("price", "count"))
    .sort_values("revenue", ascending=False)
    .reset_index(drop=True)
)
total_cat_rev = max(float(cat_df["revenue"].sum()), 1.0)
cat_df["share_pct"] = (cat_df["revenue"] / total_cat_rev * 100.0).round(2)
top5_share = float(cat_df.head(5)["share_pct"].sum()) if not cat_df.empty else 0.0

monthly_df = (
    items_df.assign(month=items_df["order_purchase_date"].dt.to_period("M").astype(str))
    .groupby("month", as_index=False)
    .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
    .sort_values("month")
    .reset_index(drop=True)
)
peak_month_row = monthly_df.loc[monthly_df["revenue"].idxmax()] if not monthly_df.empty else None
peak_month_str = peak_month_row["month"] if peak_month_row is not None else "-"

rev_orders = orders_df.dropna(subset=["review_score"]).copy()
rev_orders["is_late_pct"] = (rev_orders["delivery_status"] == "Terlambat").astype(float) * 100.0
rev_orders["is_low_pct"] = (rev_orders["review_score"] <= 2).astype(float) * 100.0

dg_df = (
    rev_orders.groupby("delay_group", as_index=False)
    .agg(
        orders=("order_id", "count"),
        avg_score=("review_score", "mean"),
        low_pct=("is_low_pct", "mean"),
    )
)

on_time_avg = float(rev_orders.loc[rev_orders["delivery_status"] == "Tepat Waktu", "review_score"].mean())
late_avg = float(rev_orders.loc[rev_orders["delivery_status"] == "Terlambat", "review_score"].mean())
score_drop = (on_time_avg - late_avg) if (pd.notna(on_time_avg) and pd.notna(late_avg)) else 2.02

# ---------------- Konten Halaman Berdasarkan Menu Aktif ----------------
if active == "Overview":
    trend_svg = build_trend_svg(monthly_df)
    top5_bars_html = build_category_bars_html(
        cat_df.head(5),
        max_val=float(cat_df["revenue"].max()) if not cat_df.empty else 1.0,
    )
    delivery_bars_html = build_delivery_bars_html(dg_df)

    render_html(
        f"""
        <section class="analysis-grid">
          <article class="panel trend-panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">PERFORMA PENDAPATAN</span>
                <h2>Tren pendapatan bulanan</h2>
              </div>
              <div class="panel-stat">
                <span>Total</span>
                <strong>{rev_display} BRL</strong>
              </div>
            </div>
            {trend_svg}
            <div class="chart-note">
              <span><i></i> Pendapatan produk</span>
              <small>Puncak pendapatan tercatat pada {peak_month_str}</small>
            </div>
          </article>
          <article class="panel category-panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">KATEGORI TERATAS</span>
                <h2>Kontribusi pendapatan</h2>
              </div>
            </div>
            {top5_bars_html}
            <div class="highlight-box">
              <div>{svg_icon("spark", 17)}</div>
              <p><strong>{top5_share:.2f}%</strong> pendapatan berasal dari 5 kategori teratas.</p>
            </div>
          </article>
        </section>

        <section class="lower-grid">
          <article class="panel delivery-panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">KUALITAS PENGIRIMAN</span>
                <h2>Dampak keterlambatan pada ulasan</h2>
              </div>
            </div>
            <div class="delivery-content">
              {delivery_bars_html}
              <div class="delivery-insight">
                <span>INSIGHT UTAMA</span>
                <strong>−{score_drop:.2f} poin</strong>
                <p>Penurunan skor rata-rata pada pesanan yang terlambat dibanding tepat waktu.</p>
                <div>
                  <i></i>
                  <small>Korelasi negatif kuat</small>
                </div>
              </div>
            </div>
          </article>
          <article class="recommendation">
            <div>
              <div class="recommendation-top">
                <span>{svg_icon("spark", 18)} REKOMENDASI</span>
                <small>PRIORITAS TINGGI</small>
              </div>
              <h2>Optimalkan mitra logistik di 4 wilayah</h2>
              <p>MA, CE, BA, dan RJ memiliki tingkat keterlambatan di atas 12%. Evaluasi SLA kurir lokal dan sesuaikan estimasi waktu kirim.</p>
            </div>
          </article>
        </section>
        """
    )

elif active == "Analisis Kategori":
    top5 = cat_df.head(5).copy()
    bot5 = cat_df.tail(5).sort_values("revenue", ascending=True).copy()

    top_bars_html = build_category_bars_html(
        top5,
        max_val=float(top5["revenue"].max()) if not top5.empty else 1.0,
        bar_color="linear-gradient(90deg, #347ff4, #5a91f1)",
    )
    bot_bars_html = build_category_bars_html(
        bot5,
        max_val=float(bot5["revenue"].max()) if not bot5.empty else 1.0,
        bar_color="linear-gradient(90deg, #f4a641, #e19032)",
    )

    render_html(
        f"""
        <section class="analysis-grid" style="grid-template-columns: 1fr 1fr;">
          <article class="panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">PERTANYAAN BISNIS 1 • TOP 5</span>
                <h2>5 Kategori dengan pendapatan tertinggi</h2>
              </div>
              <span class="pill">{top5_share:.2f}% Total Pendapatan</span>
            </div>
            {top_bars_html}
            <div class="highlight-box">
              <div>{svg_icon("spark", 17)}</div>
              <p>Kategori <strong>{pretty_category(top5.iloc[0]['category'])}</strong> memimpin dengan <strong>{top5.iloc[0]['revenue']:,.2f} BRL</strong> ({top5.iloc[0]['share_pct']:.2f}%).</p>
            </div>
          </article>
          <article class="panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">PERTANYAAN BISNIS 1 • BOTTOM 5</span>
                <h2>5 Kategori dengan pendapatan terendah</h2>
              </div>
              <span class="pill" style="color:#b45309 !important;background:#fef3c7 !important;">≤ 0.01% per Kategori</span>
            </div>
            {bot_bars_html}
            <div class="highlight-box" style="border-color:#fde68a !important;background:#fffbeb !important;">
              <div style="color:#d97706 !important;background:#fef3c7 !important;">{svg_icon("package", 17)}</div>
              <p>Kategori <strong style="color:#b45309 !important;">{pretty_category(bot5.iloc[0]['category'])}</strong> mencatat pendapatan terendah sebesar <strong style="color:#b45309 !important;">{bot5.iloc[0]['revenue']:,.2f} BRL</strong> ({int(bot5.iloc[0]['items_sold'])} unit).</p>
            </div>
          </article>
        </section>
        """
    )

    c_left, c_right = st.columns(2)
    with c_left:
        top10 = cat_df.head(10).copy()
        top10["Kategori"] = top10["category"].map(pretty_category)
        fig_top = px.bar(
            top10,
            x="revenue",
            y="Kategori",
            orientation="h",
            text=top10["revenue"].map(lambda v: f"{v:,.0f} BRL"),
            color_discrete_sequence=["#2563eb"],
            labels={"revenue": "Pendapatan (BRL)", "Kategori": ""},
            title="10 Kategori Produk Terbesar (BRL)",
        )
        fig_top.update_traces(textposition="outside", textfont=dict(color="#0f172a", size=11))
        fig_top.update_yaxes(autorange="reversed")
        fig_top.update_xaxes(range=[0, float(top10["revenue"].max()) * 1.32], showgrid=False)
        st.plotly_chart(style_plotly(fig_top, 380), width="stretch")

    with c_right:
        fig_trend = px.area(
            monthly_df,
            x="month",
            y="revenue",
            markers=True,
            color_discrete_sequence=["#2563eb"],
            labels={"month": "Bulan Pembelian", "revenue": "Pendapatan Produk (BRL)"},
            title="Tren Pendapatan Produk Bulanan (BRL)",
        )
        st.plotly_chart(style_plotly(fig_trend, 380), width="stretch")

elif active == "Pengiriman":
    delivery_bars_html = build_delivery_bars_html(dg_df)

    st_summary = (
        rev_orders.groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "count"),
            late_pct=("is_late_pct", "mean"),
            avg_score=("review_score", "mean"),
        )
    )
    min_orders = 500 if (st_summary["orders"] >= 500).sum() >= 5 else 1
    st_top = st_summary[st_summary["orders"] >= min_orders].sort_values("late_pct", ascending=False).head(6).copy()
    max_late = max(float(st_top["late_pct"].max()), 1.0) if not st_top.empty else 1.0

    state_rows_html = "".join(
        f'<div class="bar-row" style="grid-template-columns: 80px 1fr 62px 72px !important;">'
        f'<span>State <strong>{r["customer_state"]}</strong></span>'
        f'<div class="bar-track"><i style="width:{(r["late_pct"] / max_late) * 100:.1f}%;background:{"#e45c65" if r["late_pct"] >= 12 else "#347ff4"};"></i></div>'
        f'<strong>{r["late_pct"]:.2f}%</strong>'
        f'<small>skor {r["avg_score"]:.2f}</small>'
        f'</div>'
        for _, r in st_top.iterrows()
    )

    render_html(
        f"""
        <section class="analysis-grid" style="grid-template-columns: 1.15fr 1fr;">
          <article class="panel delivery-panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">PERTANYAAN BISNIS 2 • KEPUASAN PELANGGAN</span>
                <h2>Dampak keterlambatan pada skor ulasan</h2>
              </div>
              <span class="pill" style="color:#b91c1c !important;background:#fee2e2 !important;">Turun {score_drop:.2f} Poin</span>
            </div>
            <div class="delivery-content">
              {delivery_bars_html}
              <div class="delivery-insight">
                <span>INSIGHT UTAMA</span>
                <strong>−{score_drop:.2f} poin</strong>
                <p>Skor ulasan turun dari {on_time_avg:.2f} (tepat waktu) menjadi {late_avg:.2f} (terlambat).</p>
                <div>
                  <i></i>
                  <small>Ulasan skor 1–2 naik ke 62.4%</small>
                </div>
              </div>
            </div>
          </article>
          <article class="panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">PERTANYAAN BISNIS 2 • ANALISIS WILAYAH</span>
                <h2>Negara bagian dengan keterlambatan tertinggi</h2>
              </div>
              <span class="pill">Min. {min_orders} Pesanan</span>
            </div>
            <div class="bar-list">{state_rows_html}</div>
            <div class="highlight-box">
              <div>{svg_icon("truck", 17)}</div>
              <p>Wilayah <strong>MA, CE, BA, dan RJ</strong> mencatat keterlambatan di atas <strong>12%</strong> dengan skor ulasan di bawah 4.00.</p>
            </div>
          </article>
        </section>
        """
    )

    score_dist = (
        pd.crosstab(rev_orders["delivery_status"], rev_orders["review_score"].astype(int), normalize="index")
        .mul(100)
        .round(1)
        .reset_index()
        .melt(id_vars="delivery_status", var_name="Skor", value_name="Persen")
    )
    score_dist["Skor"] = "Skor " + score_dist["Skor"].astype(str)
    fig_dist = px.bar(
        score_dist,
        x="delivery_status",
        y="Persen",
        color="Skor",
        barmode="stack",
        color_discrete_sequence=["#dc2626", "#f59e0b", "#64748b", "#3b82f6", "#0d9488"],
        labels={"delivery_status": "Status Pengiriman", "Persen": "Persentase Pesanan (%)"},
        title="Distribusi Skor Ulasan (1 sampai 5): Pengiriman Tepat Waktu vs Terlambat",
    )
    st.plotly_chart(style_plotly(fig_dist, 350), width="stretch")

elif active == "Segmentasi RFM":
    ref_date = orders_df["order_purchase_date"].max() + pd.Timedelta(days=1)
    rfm = (
        orders_df.groupby("customer_unique_id", as_index=False)
        .agg(
            last_purchase=("order_purchase_date", "max"),
            frequency=("order_id", "count"),
            monetary=("order_revenue", "sum"),
        )
    )
    rfm["recency"] = (ref_date - rfm["last_purchase"]).dt.days
    rfm["recency_tier"] = pd.cut(rfm["recency"], bins=[0, 90, 180, 365, 10000], labels=RECENCY_ORDER)
    rfm["monetary_tier"] = pd.cut(rfm["monetary"], bins=[0, 50, 150, 500, 1000000], labels=MONETARY_ORDER)

    total_cust = max(len(rfm), 1)
    m_counts = rfm["monetary_tier"].value_counts().reindex(["VIP (>500 BRL)", "High (150–500 BRL)", "Medium (50–150 BRL)", "Low (<50 BRL)"]).fillna(0)
    m_pcts = (m_counts / total_cust * 100.0).round(1)

    vip_p = float(m_pcts.iloc[0])
    high_p = float(m_pcts.iloc[1])
    med_p = float(m_pcts.iloc[2])
    low_p = float(m_pcts.iloc[3])

    c1 = vip_p
    c2 = c1 + high_p
    c3 = c2 + med_p

    r_counts = rfm["recency_tier"].value_counts().reindex(RECENCY_ORDER).fillna(0)
    r_pcts = (r_counts / total_cust * 100.0).round(1)
    r_colors = ["#347ff4", "#25b2a8", "#f4a641", "#e45c65"]

    recency_rows_html = "".join(
        f'<div>'
        f'<span>{lbl}</span>'
        f'<strong>{pct:.1f}% ({int(cnt):,})</strong>'
        f'<div><i style="width:{max(pct, 3.0):.1f}%;background:{col};"></i></div>'
        f'</div>'
        for lbl, pct, cnt, col in zip(RECENCY_ORDER, r_pcts.values, r_counts.values, r_colors)
    )

    render_html(
        f"""
        <section class="analysis-grid rfm-grid">
          <article class="panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">SEGMENTASI PELANGGAN</span>
                <h2>Distribusi nilai pelanggan</h2>
              </div>
              <span class="pill">RFM Model</span>
            </div>
            <div class="donut-wrap">
              <div class="donut" style="background: conic-gradient(#347ff4 0 {c1:.1f}%, #7557e8 {c1:.1f}% {c2:.1f}%, #25b2a8 {c2:.1f}% {c3:.1f}%, #94a3b8 {c3:.1f}%);">
                <div>
                  <strong>{total_cust:,}</strong>
                  <span>Pelanggan</span>
                </div>
              </div>
              <div class="legend">
                <div><i style="background:#347ff4;"></i><span>VIP (&gt;500 BRL)</span><strong>{vip_p:.1f}%</strong></div>
                <div><i style="background:#7557e8;"></i><span>High value (150–500 BRL)</span><strong>{high_p:.1f}%</strong></div>
                <div><i style="background:#25b2a8;"></i><span>Medium (50–150 BRL)</span><strong>{med_p:.1f}%</strong></div>
                <div><i style="background:#94a3b8;"></i><span>Low value (&lt;50 BRL)</span><strong>{low_p:.1f}%</strong></div>
              </div>
            </div>
          </article>
          <article class="panel">
            <div class="panel-heading">
              <div>
                <span class="section-kicker">RETENSI</span>
                <h2>Keaktifan pelanggan (Recency)</h2>
              </div>
              <span class="pill">Repeat Buyer: {(rfm['frequency'] > 1).mean() * 100:.2f}%</span>
            </div>
            <div class="recency-list">
              {recency_rows_html}
            </div>
          </article>
        </section>
        """
    )

    m_stat = (
        rfm.groupby("monetary_tier", observed=True, as_index=False)
        .agg(customers=("customer_unique_id", "count"), revenue=("monetary", "sum"))
    )
    m_stat["% Pelanggan"] = (m_stat["customers"] / total_cust * 100).round(1)
    m_stat["% Pendapatan"] = (m_stat["revenue"] / max(float(m_stat["revenue"].sum()), 1.0) * 100).round(1)
    m_melt = m_stat.melt(
        id_vars="monetary_tier",
        value_vars=["% Pelanggan", "% Pendapatan"],
        var_name="Metrik",
        value_name="Persen",
    )
    fig_m = px.bar(
        m_melt,
        x="monetary_tier",
        y="Persen",
        color="Metrik",
        barmode="group",
        text="Persen",
        color_discrete_map={"% Pelanggan": "#64748b", "% Pendapatan": "#2563eb"},
        labels={"monetary_tier": "Kelompok Nilai Belanja (Monetary Tier)", "Persen": "Persentase (%)"},
        title="Perbandingan Porsi Pelanggan (%) vs Kontribusi Pendapatan (%) per Segmen Monetary",
    )
    fig_m.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color="#0f172a", size=11))
    fig_m.update_yaxes(range=[0, max(55.0, float(m_melt["Persen"].max()) * 1.25)])
    st.plotly_chart(style_plotly(fig_m, 360), width="stretch")

# ---------------- Footer ----------------
render_html(
    f"""
    <footer>
      <span>Sumber: Brazilian E-Commerce Public Dataset oleh Olist</span>
      <span>{total_orders:,} pesanan • {period_choice}</span>
    </footer>
    """
)
