import streamlit as st
import pandas as pd
import os

st.title("🍎 Foto-Kalorien-Tracker")

# Datei zum Speichern erstellen
DATEI = "kalorien_daten.csv"
if not os.path.exists(DATEI):
    df = pd.DataFrame(columns=["Lebensmittel", "Kalorien"])
    df.to_csv(DATEI, index=False)
df = pd.read_csv(DATEI)

# Kamera-Funktion
st.subheader("Barcode oder Essen fotografieren")
foto = st.camera_input("Kamera starten")

if foto:
    st.info("Foto erkannt! Jetzt Details eingeben:")

# Eingabe-Felder
neues_essen = st.text_input("Name (z.B. Apfel oder Barcode-Nummer)")
neue_kalorien = st.number_input("Kalorien", min_value=0, step=1)

if st.button("Speichern"):
    neue_zeile = pd.DataFrame({"Lebensmittel": [neues_essen], "Kalorien": [neue_kalorien]})
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("Gespeichert!")
    st.rerun()

# Liste anzeigen
st.divider()
st.subheader("Deine heutige Liste")
st.dataframe(df, use_container_width=True)
st.metric("Gesamt heute", f"{df['Kalorien'].sum()} kcal")

# --- NEU: LÖSCH-BUTTON ---
st.divider()
if st.button("Alle Daten löschen"):
    # Erstellt eine komplett leere Datei
    df_leer = pd.DataFrame(columns=["Lebensmittel", "Kalorien"])
    df_leer.to_csv(DATEI, index=False)
    st.warning("Alle Daten wurden entfernt!")
    st.rerun()
