import streamlit as st
import pandas as pd
import os
from datetime import date

# Seite konfigurieren
st.set_page_config(page_title="Abnehm-Coach 1550", page_icon="⚖️", layout="centered")

# --- EINSTELLUNGEN ---
TAGESZIEL = 1550  # Dein gesundes Defizit-Ziel
DATEI = "kalorien_daten.csv"

# --- DATEI-SYSTEM ---
if not os.path.exists(DATEI):
    df = pd.DataFrame(columns=["Datum", "Lebensmittel", "Kalorien"])
    df.to_csv(DATEI, index=False)

df = pd.read_csv(DATEI)
df['Datum'] = df['Datum'].astype(str)
heute_str = str(date.today())

# --- HEADER & DASHBOARD ---
st.title("⚖️ Mein Abnehm-Coach")
st.markdown(f"Dein Ziel für heute: **{TAGESZIEL} kcal**")

# Daten von heute filtern
df_heute = df[df["Datum"] == heute_str]
gegessen = df_heute["Kalorien"].sum()
uebrig = TAGESZIEL - gegessen

# Dashboard mit Ampel-Farben
m1, m2, m3 = st.columns(3)
m1.metric("Ziel", f"{TAGESZIEL} kcal")
m2.metric("Gegessen", f"{gegessen} kcal")

# Dynamische Farbe für die Rest-Kalorien (Ampel-System)
if uebrig > 200:
    farbe = "normal"  # Grün/Schwarz
    status_msg = f"Du darfst noch **{uebrig} kcal** essen. Alles im grünen Bereich! ✅"
elif 0 <= uebrig <= 200:
    farbe = "off"     # Gelb/Orange
    status_msg = f"Achtung: Nur noch **{uebrig} kcal** übrig. Fast geschafft! ⚠️"
else:
    farbe = "inverse" # Rot
    status_msg = f"Du bist **{abs(uebrig)} kcal** über deinem Defizit-Ziel! 🛑"

m3.metric("Noch offen", f"{uebrig} kcal", delta=uebrig, delta_color=farbe)

# Visueller Fortschrittsbalken
fortschritt = min(gegessen / TAGESZIEL, 1.0)
st.progress(fortschritt)
st.markdown(status_msg)

st.divider()

# --- 1. EINGABE & SCANNER ---
st.subheader("🍎 Was hast du gegessen?")

with st.expander("📷 Kamera öffnen (Barcode oder Essen)"):
    foto = st.camera_input("Kamera starten")

neues_essen = st.text_input("Name des Lebensmittels")

col1, col2 = st.columns(2)
with col1:
    menge = st.number_input("Anzahl / Menge", min_value=1, value=1, step=1)
with col2:
    einzel_kcal = st.number_input("Kalorien pro Stück", min_value=0, value=0, step=1)

total_kcal = menge * einzel_kcal

if st.button("Eintrag speichern 💾", use_container_width=True):
    if neues_essen and total_kcal > 0:
        neue_zeile = pd.DataFrame({
            "Datum": [heute_str], 
            "Lebensmittel": [f"{menge}x {neues_essen}"], 
            "Kalorien": [total_kcal]
        })
        df = pd.concat([df, neue_zeile], ignore_index=True)
        df.to_csv(DATEI, index=False)
        st.success(f"Gespeichert: {total_kcal} kcal")
        st.rerun()
    else:
        st.error("Bitte Name und Kalorien eingeben!")

# --- 2. TAGESÜBERSICHT ---
st.divider()
st.subheader("📋 Heute gegessen")

if not df_heute.empty:
    # Wir zeigen nur die relevanten Spalten schön an
    st.table(df_heute[["Lebensmittel", "Kalorien"]])
else:
    st.info("Noch keine Einträge für heute.")

# --- 3. VERLAUF & OPTIONEN ---
st.write("")
with st.expander("🕰️ Verlauf & Optionen"):
    if st.checkbox("Alle gespeicherten Tage anzeigen"):
        st.dataframe(df.sort_values("Datum", ascending=False), use_container_width=True)
    
    if st.button("Heute komplett löschen"):
        df = df[df["Datum"] != heute_str]
        df.to_csv(DATEI, index=False)
        st.rerun()

# --- MEDIZINISCHER DISCLAIMER ---
st.caption("---")
st.caption("Hinweis: Dies ist eine private Tracking-App. Kalorienberechnungen sind Schätzwerte. Für eine medizinische Beratung konsultiere bitte Fachpersonal.")
