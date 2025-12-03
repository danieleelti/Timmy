import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- 1. CONFIGURAZIONE PAGINA (PRIMA RIGA!) ---
st.set_page_config(page_title="Preventivatore TeamBuilding", page_icon="🏆", layout="centered")

# --- 2. CONFIGURAZIONE API ---
# La chiave viene letta dai "Secrets" di Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- 3. IL CERVELLO (SYSTEM PROMPT) ---
SYSTEM_PROMPT = """
SEI IL SENIOR EVENT MANAGER DI TEAMBUILDING.IT. Aiuta i clienti a scegliere i format giusti per il loro evento.

### 🎯 OBIETTIVO
Massimizzare la conversione.
1.  Proporre i format giusti (Regola dei 4).

---

### 🚦 FLUSSO DI LAVORO

**COMANDO SPECIALE "RESET" o "NUOVO":**
Se l'utente scrive "Reset", "Nuovo" o "Stop", DIMENTICA tutti i dati precedenti e ricomincia dalla FASE 0.

**FASE 0: INTERVISTA**
Ti chiami Timmy e chiedi all'utente come lo puoi aiutare.

**FASE 1: LA PROPOSTA STRATEGICA (La Regola dei 12)**
Proponi sempre una rosa di 4 FORMAT selezionati dal Database, distribuiti così:
1.  **1 BEST SELLER** (CSI, Chain Reaction, Escape Box, AperiBuilding, Cooking, Treasure Hunt, Sarabanda, Cinema, Lego, Actors Studio, Cartoon Car Race, Cocktail, Affresco, Squid Game, Bike Building, Bootcamp, Enigma, Olympic, Leonardo).
2.  **1 NOVITÀ** (Format "Novità: si" o tecnologici).
3.  **1 VIBE** (Adatti al mood).
4.  **1 SOCIAL** (Format CSR).

**VINCOLI:**
* Inverno (Nov-Mar): NO Outdoor.
* Pasti: NO Outdoor.
* Varietà: Ruota le opzioni.

**OUTPUT VISIVO PER OGNI FORMAT:**
> 🏆 **[Nome Format]**
> 📄 **Scheda:** 
> 💡 *Perché:* [Motivazione]
> ⚠️ *Note:* [Note se presenti]

---

### 💾 [DATABASE FORMAT] (Fonte Dati Unica)

Nome Format | Metodo di calcolo | Pricing | Formazione | Note | link pdf ita
5ensi | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/5ensi - TeamBuilding-it.pdf
Actors Studio | Standard | 70 | High | | https://teambuilding.it/preventivi/schede/ita/Actors Studio - TeamBuilding-it.pdf
Affresco | Standard | 75 | medium | | https://teambuilding.it/preventivi/schede/ita/Affresco - TeamBuilding-it.pdf
Agility Dog | Standard | 90 | low | | https://teambuilding.it/preventivi/schede/ita/Agility Dog - TeamBuilding-it.pdf
AI TeamBuilders | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/AI TeamBuilders - TeamBuilding-it.pdf
Aliante | Flat | 700 | High | Costo Fisso: 4000 | https://teambuilding.it/preventivi/schede/ita/Aliante - TeamBuilding-it.pdf
Animal House | Standard | 95 | Medium | | https://teambuilding.it/preventivi/schede/ita/Animal House - TeamBuilding-it.pdf
AperiBuilding | Standard | 90 | low | | https://teambuilding.it/preventivi/schede/ita/AperiBuilding - TeamBuilding-it.pdf
Auto Smash | Standard | 120 | low | Costo smaltimento auto escluso. | https://teambuilding.it/preventivi/schede/ita/Auto Smash - TeamBuilding-it.pdf
Ballando | Standard | 95 | low | | https://teambuilding.it/preventivi/schede/ita/Ballando - TeamBuilding-it.pdf
Beach Club | Standard | 75 | medium | | https://teambuilding.it/preventivi/schede/ita/Beach Club - TeamBuilding-it.pdf
Bike Building | Standard | 100 | medium | Biciclette escluse. | https://teambuilding.it/preventivi/schede/ita/Bike Building - TeamBuilding-it.pdf
Bootcamp | Standard | 85 | High | | https://teambuilding.it/preventivi/schede/ita/Bootcamp - TeamBuilding-it.pdf
Caccia all'uomo | Standard | 80 | low | | https://teambuilding.it/preventivi/schede/ita/Caccia all'uomo - TeamBuilding-it.pdf
Candid Camera | Standard | 85 | medium | | https://teambuilding.it/preventivi/schede/ita/Candid Camera - TeamBuilding-it.pdf
Cardboard World | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Cardboard World - TeamBuilding-it.pdf
Carton Boat | Standard | 70 | medium | | https://teambuilding.it/preventivi/schede/ita/Carton Boat - TeamBuilding-it.pdf
Cartoon Car Race | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Cartoon Car Race - TeamBuilding-it.pdf
Casinò | Standard | 85 | low | | https://teambuilding.it/preventivi/schede/ita/Casinò - TeamBuilding-it.pdf
Caterpillar | Flat | 300 | low | Costo fisso 3000. | https://teambuilding.it/preventivi/schede/ita/Caterpillar - TeamBuilding-it.pdf
Caterpillar Zone | Standard | 95 | medium | | https://teambuilding.it/preventivi/schede/ita/Caterpillar Zone - TeamBuilding-it.pdf
Cena con Delitto | flat | 60 | medium | Costo fisso 1800 se < 30 pax. | https://teambuilding.it/preventivi/schede/ita/Cena con Delitto - TeamBuilding-it.pdf
Chain Reaction | Standard | 75 | High | | https://teambuilding.it/preventivi/schede/ita/Chain Reaction - TeamBuilding-it.pdf
Christmas Escape | standard | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Christmas Escape - TeamBuilding-it.pdf
Christmas Sweet Lab | Standard | 100 | low | | https://teambuilding.it/preventivi/schede/ita/Christmas Sweet Lab - TeamBuilding-it.pdf
Cinema | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/Cinema - TeamBuilding-it.pdf
Circus | Standard | 110 | medium | | https://teambuilding.it/preventivi/schede/ita/Circus - TeamBuilding-it.pdf
Cocktail Building | Standard | 80 | low | | https://teambuilding.it/preventivi/schede/ita/Cocktail Building - TeamBuilding-it.pdf
Connecting Wall | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Connecting Wall - TeamBuilding-it.pdf
Cooking | Standard | 120 | High | | https://teambuilding.it/preventivi/schede/ita/Cooking - TeamBuilding-it.pdf
Cooking Mystery Box | Standard | 100 | medium | | https://teambuilding.it/preventivi/schede/ita/Cooking Mystery Box - TeamBuilding-it.pdf
Crazy Experiments | Standard | 85 | High | | https://teambuilding.it/preventivi/schede/ita/Crazy Experiments - TeamBuilding-it.pdf
Creative Recycling | Standard | 85 | medium | | https://teambuilding.it/preventivi/schede/ita/Creative Recycling - TeamBuilding-it.pdf
CSI Project | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/CSI Project - TeamBuilding-it.pdf
Csi Christmas | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/Csi Christmas - TeamBuilding-it.pdf
Darkness Experience | Standard | 70 | High | | https://teambuilding.it/preventivi/schede/ita/Darkness Experience - TeamBuilding-it.pdf
Decode Fake News | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/Decode Fake News - TeamBuilding-it.pdf
Domino Rally | Standard | 60 | medium | | https://teambuilding.it/preventivi/schede/ita/Domino Rally - TeamBuilding-it.pdf
DragonBoat | Standard | 115 | High | | https://teambuilding.it/preventivi/schede/ita/DragonBoat - TeamBuilding-it.pdf
Energy For Africa | Standard | 150 | medium | | https://teambuilding.it/preventivi/schede/ita/Energy For Africa - TeamBuilding-it.pdf
Enigma | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Enigma - TeamBuilding-it.pdf
Escape Box | Standard | 75 | High | | https://teambuilding.it/preventivi/schede/ita/Escape Box - TeamBuilding-it.pdf
Escape Dinner | Standard | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Escape Dinner - TeamBuilding-it.pdf
Family Day | flat | 80 | low | | https://teambuilding.it/preventivi/schede/ita/Family Day - TeamBuilding-it.pdf
Fashion Show | Standard | 95 | medium | | https://teambuilding.it/preventivi/schede/ita/Fashion Show - TeamBuilding-it.pdf
Ferrari Challenge | Standard | 2000 | low | | https://teambuilding.it/preventivi/schede/ita/Ferrari Challenge - TeamBuilding-it.pdf
FlashMob | Standard | 65 | low | | https://teambuilding.it/preventivi/schede/ita/FlashMob - TeamBuilding-it.pdf
Fluo Beat | Standard | 60 | low | | https://teambuilding.it/preventivi/schede/ita/Fluo Beat - TeamBuilding-it.pdf
Forno Solare | Standard | 85 | medium | | https://teambuilding.it/preventivi/schede/ita/Forno Solare - TeamBuilding-it.pdf
Go Green | Standard | 93 | low | | https://teambuilding.it/preventivi/schede/ita/Go Green - TeamBuilding-it.pdf
Green Energy | Standard | 85 | High | | https://teambuilding.it/preventivi/schede/ita/Green Energy - TeamBuilding-it.pdf
Green Grand Prix | Standard | 75 | medium | | https://teambuilding.it/preventivi/schede/ita/Green Grand Prix - TeamBuilding-it.pdf
Green Tag | Standard | 95 | low | | https://teambuilding.it/preventivi/schede/ita/Green Tag - TeamBuilding-it.pdf
Guerrilla Gardening | Standard | 0 | low | Verificare permessi. | https://teambuilding.it/preventivi/schede/ita/Guerrilla Gardening - TeamBuilding-it.pdf
Guida Sportiva | Standard | 300 | High | | https://teambuilding.it/preventivi/schede/ita/Guida Sportiva - TeamBuilding-it.pdf
Guida Neve/Ghiaccio | Standard | 700 | High | | https://teambuilding.it/preventivi/schede/ita/Guida Neve/Ghiaccio - TeamBuilding-it.pdf
Hybrid Treasure Hunt | Standard | 60 | medium | | https://teambuilding.it/preventivi/schede/ita/Hybrid Treasure Hunt - TeamBuilding-it.pdf
Ice Cream Mixology | Standard | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Ice Cream Mixology - TeamBuilding-it.pdf
Inside Team | Standard | 80 | High | | https://teambuilding.it/preventivi/schede/ita/Inside Team - TeamBuilding-it.pdf
Instabuilding Ai | Standard | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Instabuilding Ai - TeamBuilding-it.pdf
Intelligenza Artificiale | Standard | 90 | medium | | https://teambuilding.it/preventivi/schede/ita/Intelligenza Artificiale - TeamBuilding-it.pdf
Kayak | Standard | 90 | medium | | https://teambuilding.it/preventivi/schede/ita/Kayak - TeamBuilding-it.pdf
Law & Order | Standard | 60 | medium | | https://teambuilding.it/preventivi/schede/ita/Law & Order - TeamBuilding-it.pdf
Lego Building | Standard | 65 | high | | https://teambuilding.it/preventivi/schede/ita/Lego Building - TeamBuilding-it.pdf
Legolize | Standard | 60 | medium | | https://teambuilding.it/preventivi/schede/ita/Legolize - TeamBuilding-it.pdf
Leonardo da Vinci | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Leonardo da Vinci - TeamBuilding-it.pdf
LipDub | Standard | 70 | low | | https://teambuilding.it/preventivi/schede/ita/LipDub - TeamBuilding-it.pdf
Lipsync Battle | Flat | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Lipsync Battle - TeamBuilding-it.pdf
Make Your Sound | Standard | 85 | low | | https://teambuilding.it/preventivi/schede/ita/Make Your Sound - TeamBuilding-it.pdf
Mannequin Challenge | Standard | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Mannequin Challenge - TeamBuilding-it.pdf
Medieval Cart | Standard | 85 | medium | | https://teambuilding.it/preventivi/schede/ita/Medieval Cart - TeamBuilding-it.pdf
Mind Hackers | Standard | 65 | medium | | https://teambuilding.it/preventivi/schede/ita/Mind Hackers - TeamBuilding-it.pdf
Mission Impossible | Standard | 75 | medium | | https://teambuilding.it/preventivi/schede/ita/Mission Impossible - TeamBuilding-it.pdf
Mission to Mars VR | Standard | 95 | medium | | https://teambuilding.it/preventivi/schede/ita/Mission to Mars VR - TeamBuilding-it.pdf
Mosaico | Standard | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Mosaico - TeamBuilding-it.pdf
Movie Game | Flat | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Movie Game - TeamBuilding-it.pdf
Mystery Box | Standard | 100 | low | | https://teambuilding.it/preventivi/schede/ita/Mystery Box - TeamBuilding-it.pdf
Natale all'asta | Standard | 60 | low | | https://teambuilding.it/preventivi/schede/ita/Natale all'asta - TeamBuilding-it.pdf
Natale in Team | Standard | 0 | low | | https://teambuilding.it/preventivi/schede/ita/Natale in Team - TeamBuilding-it.pdf
Oggetti Misteriosi | Flat | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Oggetti Misteriosi - TeamBuilding-it.pdf
Oggetti Volanti | Standard | 0 | medium | | https://teambuilding.it/preventivi/schede/ita/Oggetti Volanti - TeamBuilding-it.pdf
Olympic Games | Standard | 75 | medium | | https://teambuilding.it/preventivi/schede/ita/Olympic Games - TeamBuilding-it.pdf
Origami | Standard | 65 | low | | https://teambuilding.it/preventivi/schede/ita/Origami - TeamBuilding-it.pdf
Pasta Building | Standard | 65 | medium | | https://teambuilding.it/preventivi/schede/ita/Pasta Building - TeamBuilding-it.pdf
Photo Competition | Standard | 90 | medium | | https://teambuilding.it/preventivi/schede/ita/Photo Competition - TeamBuilding-it.pdf
PiantiAmo | Standard | 0 | medium | Verificare stagione. | https://teambuilding.it/preventivi/schede/ita/PiantiAmo - TeamBuilding-it.pdf
Pixel Art | Flat | 60 | low | | https://teambuilding.it/preventivi/schede/ita/Pixel Art - TeamBuilding-it.pdf
Pizzaman for a Day | Standard | 100 | low | | https://teambuilding.it/preventivi/schede/ita/Pizzaman for a Day - TeamBuilding-it.pdf
Post-It Art | Standard | 65 | low | | https://teambuilding.it/preventivi/schede/ita/Post-It Art - TeamBuilding-it.pdf
Quizzone | Flat | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Quizzone - TeamBuilding-it.pdf
Quizzonline | Flat | 0 | low | | https://teambuilding.it/preventivi/schede/ita/Quizzonline - TeamBuilding-it.pdf
Rugby | Standard | 85 | medium | | https://teambuilding.it/preventivi/schede/ita/Rugby - TeamBuilding-it.pdf
Sailing | Standard | 250 | medium | | https://teambuilding.it/preventivi/schede/ita/Sailing - TeamBuilding-it.pdf
Sailing Garda | Standard | 200 | medium | | https://teambuilding.it/preventivi/schede/ita/Sailing Garda - TeamBuilding-it.pdf
Santa's Helper | Standard | 95 | low | | https://teambuilding.it/preventivi/schede/ita/Santa's Helper - TeamBuilding-it.pdf
Sarabanda | flat | 70 | low | | https://teambuilding.it/preventivi/schede/ita/Sarabanda - TeamBuilding-it.pdf
Scolpisci | Standard | 85 | low | | https://teambuilding.it/preventivi/schede/ita/Scolpisci - TeamBuilding-it.pdf
Shackleton | Standard | 110 | high | | https://teambuilding.it/preventivi/schede/ita/Shackleton - TeamBuilding-it.pdf
Slitte Pazze | Standard | 90 | high | | https://teambuilding.it/preventivi/schede/ita/Slitte Pazze - TeamBuilding-it.pdf
Smart Team Challenge | Standard | 90 | high | | https://teambuilding.it/preventivi/schede/ita/Smart Team Challenge - TeamBuilding-it.pdf
Social Team Building | Standard | 150 | high | | https://teambuilding.it/preventivi/schede/ita/Social Team Building - TeamBuilding-it.pdf
Softair LaserTag | Standard | 90 | medium | | https://teambuilding.it/preventivi/schede/ita/Softair LaserTag - TeamBuilding-it.pdf
Squid Game | Standard | 85 | low | | https://teambuilding.it/preventivi/schede/ita/Squid Game - TeamBuilding-it.pdf
Street Fundraising | Standard | 95 | low | | https://teambuilding.it/preventivi/schede/ita/Street Fundraising - TeamBuilding-it.pdf
Stuntman | Standard | 150 | low | | https://teambuilding.it/preventivi/schede/ita/Stuntman - TeamBuilding-it.pdf
Survival | Standard | 90 | high | | https://teambuilding.it/preventivi/schede/ita/Survival - TeamBuilding-it.pdf
Sushi San | Standard | 110 | low | | https://teambuilding.it/preventivi/schede/ita/Sushi San - TeamBuilding-it.pdf
SWAT | Standard | 95 | high | | https://teambuilding.it/preventivi/schede/ita/SWAT - TeamBuilding-it.pdf
Tableau Vivant | Standard | 85 | low | | https://teambuilding.it/preventivi/schede/ita/Tableau Vivant - TeamBuilding-it.pdf
Talent Factory | Standard | 82 | low | | https://teambuilding.it/preventivi/schede/ita/Talent Factory - TeamBuilding-it.pdf
Team Beat | Standard | 80 | medium | | https://teambuilding.it/preventivi/schede/ita/Team Beat - TeamBuilding-it.pdf
The Box | Standard | 70 | low | | https://teambuilding.it/preventivi/schede/ita/The Box - TeamBuilding-it.pdf
The Comic Side of Work | Standard | 80 | high | | https://teambuilding.it/preventivi/schede/ita/The Comic Side of Work - TeamBuilding-it.pdf
Tinkering | Standard | 75 | high | | https://teambuilding.it/preventivi/schede/ita/Tinkering - TeamBuilding-it.pdf
Tombola Beat | Flat | 45 | low | | https://teambuilding.it/preventivi/schede/ita/Tombola Beat - TeamBuilding-it.pdf
Treasure Hunt | Standard | 75 | low | | https://teambuilding.it/preventivi/schede/ita/Treasure Hunt - TeamBuilding-it.pdf
Unlock and Drink | Standard | 90 | medium | | https://teambuilding.it/preventivi/schede/ita/Unlock and Drink - TeamBuilding-it.pdf
Vertical Garden | Standard | 95 | medium | | https://teambuilding.it/preventivi/schede/ita/Vertical Garden - TeamBuilding-it.pdf
Vintage Tours | Standard | 250 | low | | https://teambuilding.it/preventivi/schede/ita/Vintage Tours - TeamBuilding-it.pdf
Virtual Escape Box | Standard | 60 | low | | https://teambuilding.it/preventivi/schede/ita/Virtual Escape Box - TeamBuilding-it.pdf
Yacht Day | Standard | 0 | medium | Prezzo indicativo. | https://teambuilding.it/preventivi/schede/ita/Yacht Day - TeamBuilding-it.pdf
"""

# --- 4. AVVIO DELL'APP ---
genai.configure(api_key=api_key)

# SICUREZZA (Sblocco totale)
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash", # Usa Flash per stabilità, o "gemini-1.5-pro"
  generation_config={"temperature": 0.0},
  system_instruction=SYSTEM_PROMPT,
  safety_settings=safety_settings,
)

# LOGIN
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Area Riservata")
    pwd = st.text_input("Inserisci Password Staff", type="password")
    if st.button("Accedi"):
        if pwd == PASSWORD_SEGRETA:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata")
    st.stop()

# INTERFACCIA
st.title("🏆 Preventivatore AI")
st.caption("Assistente Virtuale Senior - Uso Interno")

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Ciao! Sono pronto. Dimmi numero pax, data e obiettivo."
    st.session_state.messages.append({"role": "model", "content": welcome})

# Mostra cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Scrivi qui la richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Reset
    if prompt.lower().strip() in ["reset", "nuovo", "cancella", "stop"]:
        st.session_state.messages = []
        st.rerun()

    with st.chat_message("model"):
        with st.spinner("Elaborazione..."):
            try:
                history_gemini = []
                for m in st.session_state.messages:
                    if m["role"] != "model": 
                        history_gemini.append({"role": "user", "parts": [m["content"]]})
                    else:
                        history_gemini.append({"role": "model", "parts": [m["content"]]})
                
                chat = model.start_chat(history=history_gemini[:-1])
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
                
            except Exception as e:
                st.error(f"Errore: {e}")