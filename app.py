import streamlit as st
import pandas as pd
import os
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Dark Calorie Crypt", page_icon="🦇", layout="centered")

# 2. SICHERHEITSKLASSE & HASH
class PasswordSecurity:
    def __init__(self):
        self.ph = PasswordHasher()

    def create_hash(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        try:
            return self.ph.verify(stored_hash, provided_password)
        except (VerifyMismatchError, Exception):
            return False

# Dein neues Siegel (Argon2 Hash)
RICHTIGER_HASH = "$argon2id$v=19$m=65536,t=3,p=4$0tEES9HI0I0E4BdphRMZIA$obAzWCMG4UiRvNafxgy1xToF6dzaCVeha3plJKf7Jio"

def check_password():
    security = PasswordSecurity()
    
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #8b0000;'>Wer betritt die Krypta?</h2>", unsafe_allow_html=True)
        pwd_input = st.text_input("Geheimnis", type="password", placeholder="Gib dein Passwort ein...")
        
        if st.button("Eintreten", use_container_width=True):
            if security.verify_password(RICHTIGER_HASH, pwd_input):
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Der Schatten verweigert dir den Zutritt.")
        return False
    return True

# 3. HAUPTPROGRAMM (Nur nach Login sichtbar)
if check_password():
    
    # --- GOTHIC DESIGN (CSS) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0a0a0a; color: #b3b3b3; font-family: 'Georgia', serif; }
        [data-testid="stMetricValue"] { color: #8b0000 !important; font-size: 2rem !important; }
        .stButton>button { width: 100%; border-radius: 5px; background-color: #4a0404; color: #e0e0e0; border: 1px solid #8b0000; }
        .stButton>button:hover { background-color: #8b0000; color: white; border: 1px solid #ff0000; }
        input { background-color: #1a1a1a !important; color: #e0e0e0 !important; border: 1px solid #333 !important; }
        .stProgress > div > div > div > div { background-color: #8b0000; }
        </style>
        """, unsafe_allow_html=True)

    # --- EINSTELLUNGEN & DATEN ---
    TAGESZIEL = 1550
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATEI = os.path.join(BASE_DIR, "kalorien_daten.csv")

    if not os.path.exists(DATEI):
        df = pd.DataFrame(columns=["Datum", "Lebensmittel", "Kalorien"])
        df.to_csv(DATEI, index=False)
    
    df = pd.read_csv(DATEI)
    df['Datum'] = df['Datum'].astype(str)
    heute_str = str(date.today())

    # --- HEADER ---
    st.markdown("<h1 style='text-align: center; color: #8b0000;'>🦇 Dark Calorie Crypt 🦇</h1>", unsafe_allow_html=True)

    # --- DASHBOARD ---
    df_heute = df[df["Datum"] == heute_str]
    gegessen = df_heute["Kalorien"].sum()
    uebrig = TAGESZIEL - gegessen

    c1, c2, c3 = st.columns(3)
    c1.metric("Limit", f"{TAGESZIEL}")
    c2.metric("Opfer", f"{gegessen}")
    c3.metric("Rest", f"{uebrig}")

    st.progress(min(gegessen / TAGESZIEL, 1.0))
    st.divider()

    # --- EINGABE ---
    st.subheader("🌑 Neues Opfer eintragen")
    neues_essen = st.text_input("Name der Speise")
    
    einheit = st.radio("Einheit wählen", ["Stück", "Gramm"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        menge_label = "Anzahl" if einheit == "Stück" else "Gewicht (g)"
        menge = st.number_input(menge_label, min_value=1, value=1 if einheit == "Stück" else 100, step=1)
    with col2:
        kcal_label = "Kalorien pro Stück" if einheit == "Stück" else "Kalorien pro 100g"
        einzel_kcal = st.number_input(kcal_label, min_value=0, value=0, step=1)

    if einheit == "Stück":
        total_kcal = menge * einzel_kcal
        eintrag_name = f"{menge}x {neues_essen}"
    else:
        total_kcal = (menge / 100) * einzel_kcal
        eintrag_name = f"{menge}g {neues_essen}"

    if st.button("In der Krypta speichern 💾"):
        if neues_essen and total_kcal > 0:
            neue_zeile = pd.DataFrame({
                "Datum": [heute_str], 
                "Lebensmittel": [eintrag_name], 
                "Kalorien": [round(total_kcal, 1)]
            })
            df = pd.concat([df, neue_zeile], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Eintrag sicher verwahrt.")
            st.rerun() # Seite neu laden, um Metriken zu aktualisieren

    # --- LISTE ---
    st.divider()
    st.subheader("📜 Heutige Chronik")
    if not df_heute.empty:
        st.table(df_heute[["Lebensmittel", "Kalorien"]])
    else:
        st.info("Noch keine Seelen... äh, Kalorien gefangen.")

    # --- FOOTER & KAMERA ---
    with st.expander("📷 Scanner der Finsternis"):
        st.camera_input("Foto aufnehmen", key="kamera")

    st.write("")
    if st.button("Abmelden / Krypta verlassen"):
        del st.session_state["password_correct"]
        st.rerun()
