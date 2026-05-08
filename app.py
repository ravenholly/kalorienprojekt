import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Dark Calorie Crypt", page_icon="🐦‍⬛", layout="centered")

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
        for col in columns:
            if col not in df.columns:
                df[col] = "Mittagessen"
    return df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# --- GOTHIC DESIGN (CSS) - GLOBAL geladen für Login & App ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almendra:ital,wght@0,400;0,700;1,400;1,700&family=Cinzel:wght@400;700&display=swap');

    /* Shimmer Animation */
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Spezial-Shimmer für den Balken: Nur die Farbe bewegt sich */
    @keyframes shimmer-bar {
        0% { background-position: 0 0, 0 0, -200% 0; }
        100% { background-position: 0 0, 0 0, 200% 0; }
    }

    /* Magischer Glitzer-Schatten */
    @keyframes magic-aura {
        0%, 100% { box-shadow: 0 0 10px #ff007f, 0 0 5px #fff; }
        50% { box-shadow: 0 0 20px #ff85c0, 0 0 10px #fff; }
    }

    /* Funkelnde Punkte (Sparkle) durch Größenänderung */
    @keyframes sparkle {
        0%, 100% { background-size: 18px 18px, 28px 28px, 200% 100%; opacity: 1; }
        50% { background-size: 25px 25px, 20px 20px, 200% 100%; opacity: 0.8; }
    }

    /* Haupt-Hintergrund: Zentrum etwas heller für bessere Sichtbarkeit auf Handys */
    .stApp { 
        background: radial-gradient(circle at center, #3a0820 0%, #0a0505 60%, #000000 100%); 
        color: #d3d3d3; 
        font-family: 'Almendra', serif; 
    }

    /* Überschriften (GoT Style) */
    h1, h2, h3, h5 { 
        font-family: 'Cinzel', serif; 
        color: #ff85c0; 
        text-shadow: 2px 2px 10px rgba(255, 133, 192, 0.5); 
        text-transform: uppercase;
        text-align: center;
    }

    /* Metriken */
    div[data-testid="stMetric"] {
        background: rgba(35, 5, 20, 0.5);
        border: 1px solid #db7093;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(219, 112, 147, 0.2); 
    }
    [data-testid="stMetricValue"] { 
        color: #ffb6c1 !important; 
        font-size: 2.2rem !important; 
        text-shadow: 0 0 10px rgba(255, 182, 193, 0.4);
    }

    /* Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 0px; 
        background: linear-gradient(90deg, #1a050d, #3d0d1c, #1a050d);
        background-size: 200% 100%;
        color: #ffb6c1; 
        border: 1px solid #db7093;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        animation: shimmer 3s infinite linear;
        background-image: linear-gradient(90deg, #250a15, #db7093, #ffb6c1, #db7093, #250a15); 
        color: #ffffff; 
        box-shadow: 0 0 20px rgba(219, 112, 147, 0.4); 
        transform: translateY(-2px);
        border-color: #ffb6c1; 
    }

    /* Inputs & Sidebar */
    input { 
        background-color: #000 !important; 
        color: #ffb6c1 !important; 
        border: 1px solid #db7093 !important; 
    }
    .stProgress > div > div > div > div { 
        background: 
            radial-gradient(circle, rgba(255,255,255,0.7) 1.5px, transparent 2px),
            radial-gradient(circle, rgba(255,255,255,0.4) 1px, transparent 1.5px),
            linear-gradient(90deg, #ff007f, #db7093, #ff007f); 
        background-size: 18px 18px, 28px 28px, 200% 100%;
        background-position: 0 0, 8px 8px, 0 0;
        animation: shimmer-bar 4s infinite linear, sparkle 3s infinite ease-in-out, magic-aura 2s infinite ease-in-out;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    [data-testid="stSidebar"] { 
        background-color: #0a0005; 
        border-right: 2px solid #db7093; 
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #050505; }
    ::-webkit-scrollbar-thumb { background: #4a0404; }
    </style>
    """, unsafe_allow_html=True)

if check_password():
    # --- EINSTELLUNGEN & DATEN ---
    TAGESZIEL = 1550
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATEI = os.path.join(BASE_DIR, "kalorien_daten.csv")
    PREDEFINED_DATEI = os.path.join(BASE_DIR, "predefined_foods.csv")

    # Lade Haupt-Kaloriendaten
    df = load_data(DATEI, ["Datum", "Lebensmittel", "Kalorien", "Kategorie"])
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
        
        if "aktuelle_kat" not in st.session_state or st.session_state.aktuelle_kat not in ["Frühstück", "Mittagessen", "Abendessen"]:
            st.session_state.aktuelle_kat = "Mittagessen"
        
        kat_wahl = st.selectbox("📍 Kategorie für manuelle Eingabe:", 
                                ["Frühstück", "Mittagessen", "Abendessen"],
                                index=["Frühstück", "Mittagessen", "Abendessen"].index(st.session_state.aktuelle_kat))
        st.session_state.aktuelle_kat = kat_wahl
        st.divider()

        if df_predefined.empty:
            st.info("Deine Vorratskammer ist leer. Speichere Lebensmittel im Hauptmenü als Favorit!")
        else:
            for index, row in df_predefined.iterrows():
                with st.container():
                    # Berechnung der Gesamtkalorien für die Anzeige in der Sidebar
                    fav_total = (row['Menge'] / 100 * row['Kalorien_pro_Einheit']) if row['Einheit'] == "Gramm" else (row['Menge'] * row['Kalorien_pro_Einheit'])
                    
                    # Layout für jeden Favoriten: Name und zwei Buttons
                    st.markdown(f"**{row['Name']}**  \n<small>{row['Menge']}{'g' if row['Einheit'] == 'Gramm' else 'x'} (Gesamt: {round(fav_total, 1)} kcal)</small>", unsafe_allow_html=True)
                    
                    c_add, c_del = st.columns([0.8, 0.2])
                    
                    def add_entry(cat):
                        kcal_val = (row['Menge'] / 100 * row['Kalorien_pro_Einheit']) if row['Einheit'] == "Gramm" else (row['Menge'] * row['Kalorien_pro_Einheit'])
                        food_lbl = f"{row['Menge']}g {row['Name']}" if row['Einheit'] == "Gramm" else f"{row['Menge']}x {row['Name']}"
                        
                        new_entry = pd.DataFrame({
                            "Datum": [heute_str], 
                            "Lebensmittel": [food_lbl], 
                            "Kalorien": [round(kcal_val, 1)],
                            "Kategorie": [cat]
                        })
                        full_df = pd.concat([df, new_entry], ignore_index=True)
                        save_data(full_df, DATEI)
                        st.rerun()

                    if c_add.button(f"Hinzufügen", key=f"add_{index}", use_container_width=True): 
                        add_entry(st.session_state.aktuelle_kat)
                    if c_del.button("🗑️", key=f"del_{index}", use_container_width=True):
                        df_predefined = df_predefined.drop(index)
                        save_data(df_predefined, PREDEFINED_DATEI)
                        st.rerun()
                st.divider()

        st.write("")
        if st.button("Abmelden"):
            del st.session_state["password_correct"]
            st.rerun()


    # --- HEADER ---
    st.markdown("<h1 style='text-align: center; color: #8b0000;'>🐦‍⬛ Dark Calorie Crypt <span style='display:inline-block; transform: scaleX(-1);'>🐦‍⬛</span></h1>", unsafe_allow_html=True)

    # --- DASHBOARD ---
    df_heute = df[df["Datum"] == heute_str]
    gegessen = df_heute["Kalorien"].sum()
    uebrig = TAGESZIEL - gegessen

    c1, c2, c3 = st.columns(3)
    c1.metric("Limit", f"{TAGESZIEL}")
    c2.metric("Opfer", f"{round(gegessen, 1)}")
    c3.metric("Rest", f"{round(uebrig, 1)}")

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
        menge = st.number_input(menge_label, min_value=0.5, value=1.0 if einheit == "Stück" else 100.0, step=0.5)
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
                "Kalorien": [final_kcal],
                "Kategorie": [kat_wahl]
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
        for kat in ["Frühstück", "Mittagessen", "Abendessen"]:
            kat_entries = df_heute[df_heute["Kategorie"] == kat]
            if not kat_entries.empty:
                st.markdown(f"<h5 style='color: #8b0000; border-bottom: 1px solid #333; margin-top: 10px;'>{kat}</h5>", unsafe_allow_html=True)
                for index, row in kat_entries.iterrows():
                    c_info, c_del = st.columns([0.85, 0.15])
                    c_info.write(f"**{row['Lebensmittel']}**: {round(row['Kalorien'], 1)} kcal")
                    if c_del.button("🗑️", key=f"del_entry_{index}"):
                        df = df.drop(index)
                        save_data(df, DATEI)
                        st.rerun()
    else:
        st.info("Noch keine Seelen... äh, Kalorien gefangen.")
