import streamlit as st
import pandas as pd
import os
from datetime import date

# Seite konfigurieren
st.set_page_config(page_title="Mein Kalorien-Coach", page_icon="⚖️")

# --- EINSTELLUNGEN ---
TAGESZIEL = 1700
DATEI = "kalorien_daten.csv"

# --- DATEI-SYSTEM ---
if not os.path.exists(DATEI):
    df = pd.DataFrame(columns=["Datum", "Lebensmittel", "Kalorien"])
    df.to_csv(DATEI, index=False)

# Daten laden
df = pd.read_csv(DATEI)
# Sicherstellen, dass das Datum als Text verglichen werden kann
df['Datum'] = df['Datum'].astype(str)
heute_str = str(date.today())

# --- HEADER & DASHBOARD ---
st.title("⚖️ Mein Kalorien-Coach")

# Nur die Daten von heute filtern für die Berechnung
df_heute = df[df["Datum"] == heute_str]
gegessen = df_heute["Kalorien"].sum()
uebrig = TAGESZIEL - gegessen

# Dashboard mit drei Spalten
m1, m2, m3 = st.columns(3)
m1.metric("Tagesziel", f"{TAGESZIEL} kcal")
m2.metric("Gegessen", f"{gegessen} kcal")
m3.metric("Noch offen", f"{uebrig} kcal", delta_color="normal")

# Fortschrittsbalken
fortschritt = min(gegessen / TAGESZIEL, 1.0)
st.progress(fortschritt)

if uebrig < 0:
    st.error(f"⚠️ Du bist {abs(uebrig)} kcal über deinem Ziel!")
elif uebrig < 200:
    st.warning(f"Fast geschafft! Nur noch {uebrig} kcal übrig.")
else:
    st.success(f"Du hast noch {uebrig} kcal für heute.")

st.divider()

# --- 1. SCANNER / FOTO ---
with st.expander("📷 Kamera öffnen zum Scannen/Fotografieren"):
    foto = st.camera_input("Kamera starten")

# --- 2. EINGABE ---
st.subheader("Neuen Eintrag hinzufügen")
neues_essen = st.text_input("Was hast du gegessen?")

c1, c2 = st.columns(2)
with c1:
    menge = st.number_input("Anzahl / Menge", min_value=1, value=1)
with c2:
    einzel_kcal = st.number_input("Kalorien pro Stück", min_value=0, value=0)

total_kcal = menge * einzel_kcal

if st.button("Speichern 💾", use_container_width=True):
    if neues_essen and total_kcal > 0:
        neue_zeile = pd.DataFrame({
            "Datum": [heute_str], 
            "Lebensmittel": [f"{menge}x {neues_essen}"], 
            "Kalorien": [total_kcal]
        })
        df = pd.concat([df, neue_zeile], ignore_index=True)
        df.to_csv(DATEI, index=False)
        st.success("Eintrag gespeichert!")
        st.rerun()

# --- 3. TAGESÜBERSICHT ---
st.divider()
st.subheader(f"📋 Das hast du heute ({heute_str}) gegessen:")

if not df_heute.empty:
    st.table(df_heute[["Lebensmittel", "Kalorien"]])
else:
    st.info("Heute noch keine Einträge.")

# --- 4. OPTIONEN ---
st.write("")
if st.checkbox("Verlauf der letzten Tage anzeigen"):
    st.dataframe(df.sort_values("Datum", ascending=False), use_container_width=True)

if st.button("Tagesliste leeren"):
    # Löscht nur die Einträge von heute
    df = df[df["Datum"] != heute_str]
    df.to_csv(DATEI, index=False)
    st.rerun()
