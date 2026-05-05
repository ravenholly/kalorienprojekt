import streamlit as st
import pandas as pd
import os
from datetime import date

# 1. Seite professionell konfigurieren
st.set_page_config(page_title="Kalorien Coach", page_icon="🍎", layout="centered")

# Design-Anpassung (Macht den Button schöner)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- EINSTELLUNGEN ---
TAGESZIEL = 1550
DATEI = "kalorien_daten.csv"

# --- DATEI-SYSTEM ---
if not os.path.exists(DATEI):
    df = pd.DataFrame(columns=["Datum", "Lebensmittel", "Kalorien"])
    df.to_csv(DATEI, index=False)
df = pd.read_csv(DATEI)
df['Datum'] = df['Datum'].astype(str)
heute_str = str(date.today())

# --- DASHBOARD ---
st.title("🍎 Kalorien Coach")
df_heute = df[df["Datum"] == heute_str]
gegessen = df_heute["Kalorien"].sum()
uebrig = TAGESZIEL - gegessen

# Anzeige in Kacheln
col1, col2 = st.columns(2)
with col1:
    st.metric("Gegessen", f"{gegessen} kcal")
with col2:
    farbe = "normal" if uebrig > 0 else "inverse"
    st.metric("Noch offen", f"{uebrig} kcal", delta=uebrig, delta_color=farbe)

# Fortschrittsbalken
fortschritt = min(gegessen / TAGESZIEL, 1.0)
st.progress(fortschritt)

st.divider()

# --- EINGABE ---
st.subheader("✍️ Eintrag hinzufügen")
neues_essen = st.text_input("Was hast du gegessen?", placeholder="z.B. Apfel")

c1, c2 = st.columns(2)
with c1:
    menge = st.number_input("Menge", min_value=1, value=1)
with c2:
    einzel_kcal = st.number_input("kcal pro Stück", min_value=0, value=0)

if st.button("Speichern 💾"):
    if neues_essen and (menge * einzel_kcal) > 0:
        neue_zeile = pd.DataFrame({
            "Datum": [heute_str], 
            "Lebensmittel": [f"{menge}x {neues_essen}"], 
            "Kalorien": [menge * einzel_kcal]
        })
        df = pd.concat([df, neue_zeile], ignore_index=True)
        df.to_csv(DATEI, index=False)
        st.success("Erfolgreich gespeichert!")
        st.rerun()

# --- LISTE ---
st.divider()
st.subheader("📋 Heute gegessen")
if not df_heute.empty:
    st.table(df_heute[["Lebensmittel", "Kalorien"]])
else:
    st.info("Noch keine Einträge für heute.")

with st.expander("📷 Kamera nutzen"):
    st.camera_input("Foto machen", key="cam")
