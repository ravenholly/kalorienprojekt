import streamlit as st
import pandas as pd
import os
import hashlib
import requests
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

def get_product_info(barcode):
    """Holt Produktdaten von Open Food Facts."""
    barcode = str(barcode).strip()
    if not barcode:
        return None, None, None
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        headers = {"User-Agent": "DarkCalorieCrypt/1.0 (Windows)"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                name = product.get("product_name_de") or product.get("product_name") or "Unbekanntes Opfer"
                nutriments = product.get("nutriments", {})
                
                kcal = 0.0
                # 1. Versuch: Kalorien (kcal) direkt finden
                for key in ["energy-kcal_100g", "energy-kcal_serving", "energy-kcal"]:
                    val = nutriments.get(key)
                    if val is not None:
                        try:
                            kcal = float(val)
                            break
                        except (ValueError, TypeError):
                            continue

                # 2. Versuch: Wenn kcal immer noch 0.0, nach kJ suchen (1 kcal = 4.184 kJ)
                if kcal == 0.0:
                    for key in ["energy-kj_100g", "energy-kj_serving", "energy_100g", "energy_serving"]:
                        val = nutriments.get(key)
                        if val is not None:
                            try:
                                kcal = float(val) / 4.184
                                break
                            except (ValueError, TypeError):
                                continue
                
                image = product.get("image_front_small_url")
                return name, kcal, image
    except requests.exceptions.RequestException:
        st.error("Verbindung zur Datenbank fehlgeschlagen.")
    except Exception as e:
        st.error(f"Fehler: {e}")
    return None, None, None

# --- HILFSFUNKTIONEN ---
def load_data(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
    else:
        df = pd.read_csv(file_path)
    return df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)


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
        [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #8b0000; }
        </style>
        """, unsafe_allow_html=True)

    # --- EINSTELLUNGEN & DATEN ---
    TAGESZIEL = 1550
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATEI = os.path.join(BASE_DIR, "kalorien_daten.csv")
    PREDEFINED_DATEI = os.path.join(BASE_DIR, "predefined_foods.csv")

    # Lade Haupt-Kaloriendaten
    df = load_data(DATEI, ["Datum", "Lebensmittel", "Kalorien"])
    df['Datum'] = df['Datum'].astype(str)
    
    # Lade vordefinierte Lebensmittel
    df_predefined = load_data(PREDEFINED_DATEI, ["Name", "Menge", "Einheit", "Kalorien_pro_Einheit"])

    # Session State für Barcode-Suche initialisieren
    if "bc_name" not in st.session_state: st.session_state.bc_name = ""
    if "bc_kcal" not in st.session_state: st.session_state.bc_kcal = 0.0 # Initialisiere als Float

    heute_str = str(date.today())

    # --- SIDEBAR: SCHNELLE AUSWAHL (FAVORITEN) ---
    with st.sidebar:
        st.markdown("<h2 style='color: #8b0000;'>🧛 Vorräte</h2>", unsafe_allow_html=True)
        if df_predefined.empty:
            st.info("Deine Vorratskammer ist leer. Speichere Lebensmittel im Hauptmenü als Favorit!")
        else:
            for index, row in df_predefined.iterrows():
                with st.container():
                    # Berechnung der Gesamtkalorien für die Anzeige in der Sidebar
                    fav_total = (row['Menge'] / 100 * row['Kalorien_pro_Einheit']) if row['Einheit'] == "Gramm" else (row['Menge'] * row['Kalorien_pro_Einheit'])
                    
                    # Layout für jeden Favoriten: Name und zwei Buttons (Hinzufügen/Löschen)
                    st.markdown(f"**{row['Name']}**  \n<small>{row['Menge']}{'g' if row['Einheit'] == 'Gramm' else 'x'} (Gesamt: {round(fav_total, 1)} kcal)</small>", unsafe_allow_html=True)
                    
                    c_add, c_del = st.columns(2)
                    if c_add.button("➕", key=f"add_{index}"):
                        # Berechnung für den heutigen Eintrag
                        total_kcal = (row['Menge'] / 100 * row['Kalorien_pro_Einheit']) if row['Einheit'] == "Gramm" else (row['Menge'] * row['Kalorien_pro_Einheit'])
                        label = f"{row['Menge']}g {row['Name']}" if row['Einheit'] == "Gramm" else f"{row['Menge']}x {row['Name']}"
                        
                        neue_zeile = pd.DataFrame({
                            "Datum": [heute_str], 
                            "Lebensmittel": [label], 
                            "Kalorien": [round(total_kcal, 1)]
                        })
                        df = pd.concat([df, neue_zeile], ignore_index=True)
                        save_data(df, DATEI)
                        st.rerun()
                    
                    if c_del.button("🗑️", key=f"del_{index}"):
                        df_predefined = df_predefined.drop(index)
                        save_data(df_predefined, PREDEFINED_DATEI)
                        st.rerun()
                st.divider()

        st.write("")
        if st.button("Abmelden"):
            del st.session_state["password_correct"]
            st.rerun()


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
    st.subheader("🌑 Neues Opfer rufen")
    
    # Barcode-Suche
    barcode_input = st.text_input("Barcode-Nummer (EAN) eingeben")
    if st.button("Relikt prüfen 🔍"):
        # Felder immer zuerst leeren, bevor eine neue Suche gestartet wird
        st.session_state.bc_name = ""
        st.session_state.bc_kcal = 0.0

        if barcode_input:
            with st.spinner("Suche in der Unterwelt..."):
                name, kcal, image = get_product_info(barcode_input)
                if name:
                    st.session_state.bc_name = name
                    st.session_state.bc_kcal = kcal
                    if image:
                        st.image(image, width=100)
                    st.success(f"Gefunden: {name}")
                else:
                    st.error("Dieses Relikt ist unbekannt.")

    st.divider()
    neues_essen = st.text_input("Name der Speise", value=st.session_state.bc_name)
    
    einheit = st.radio("Einheit wählen", ["Stück", "Gramm"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        menge_label = "Anzahl" if einheit == "Stück" else "Gewicht (g)"
        menge = st.number_input(menge_label, min_value=1, value=1 if einheit == "Stück" else 100, step=1)
    with col2:
        kcal_label = "Kalorien pro Stück" if einheit == "Stück" else "Kalorien pro 100g"
        einzel_kcal = st.number_input(kcal_label, min_value=0.0, value=float(st.session_state.bc_kcal), step=0.1, format="%.1f")

    als_favorit = st.checkbox("Dauerhaft in Vorräte (Sidebar) aufnehmen?")

    if einheit == "Stück":
        total_kcal = menge * einzel_kcal
        eintrag_name = f"{menge}x {neues_essen}"
    else:
        total_kcal = (menge / 100) * einzel_kcal
        eintrag_name = f"{menge}g {neues_essen}"

    # Wir runden auf eine Nachkommastelle für die Chronik
    final_kcal = round(total_kcal, 1)

    # Live-Vorschau der berechneten Kalorien
    st.info(f"⚖️ **Berechnete Opfergabe:** {final_kcal} kcal")

    if st.button("In der Krypta speichern 💾", use_container_width=True):
        if neues_essen:
            # In Tagesliste speichern
            neue_zeile = pd.DataFrame({
                "Datum": [heute_str], 
                "Lebensmittel": [eintrag_name], 
                "Kalorien": [final_kcal]
            })
            df = pd.concat([df, neue_zeile], ignore_index=True)
            save_data(df, DATEI)
            
            # Optional: In Favoriten (Sidebar) speichern
            if als_favorit:
                neu_fav = pd.DataFrame([{"Name": neues_essen, "Menge": menge, "Einheit": einheit, "Kalorien_pro_Einheit": einzel_kcal}])
                df_predefined = pd.concat([df_predefined, neu_fav], ignore_index=True)
                save_data(df_predefined, PREDEFINED_DATEI)
                
            # Felder nach Speichern leeren
            st.session_state.bc_name = "" # Leert den Namen
            st.session_state.bc_kcal = 0.0 # Setzt Kalorien auf 0.0
            
            st.success("Eintrag sicher verwahrt.")
            st.rerun() # Seite neu laden, um Metriken zu aktualisieren

    # --- LISTE ---
    st.divider()
    st.subheader("📜 Heutige Chronik")
    if not df_heute.empty:
        for index, row in df_heute.iterrows():
            c_info, c_del = st.columns([0.85, 0.15])
            c_info.write(f"**{row['Lebensmittel']}**: {row['Kalorien']} kcal")
            if c_del.button("🗑️", key=f"del_entry_{index}"):
                df = df.drop(index)
                save_data(df, DATEI)
                st.rerun()
    else:
        st.info("Noch keine Seelen... äh, Kalorien gefangen.")
