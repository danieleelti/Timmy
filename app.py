import streamlit as st
import google.generativeai as genai
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- IMPORT DATABASE ---
# Assicurati che il file format.py sia nella stessa cartella
from format import database_attivita

# --- CONFIGURAZIONE ---
logo_url = "https://www.teambuilding.it/sito/wp-content/uploads/2023/07/cropped-favicon-32x32.png"

st.set_page_config(page_title="Timmy", page_icon="🦁", layout="centered")

# --- DEBUG LATERALE (Verifica caricamento dati) ---
#try:
#   dati_json = json.loads(database_attivita)
#    numero_format = len(dati_json)
#    st.sidebar.success(f"✅ Catalogo Attivo: {numero_format} format.")
# except:
#    st.sidebar.error("⚠️ Errore lettura CSV/Database.")
# --- FINE BLOCCO DEBUG ---

# --- 2. CONFIGURAZIONE API ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- 3. ISTRUZIONI DI SISTEMA ---
# Usiamo istruzioni chiare per guidare il modello senza bloccarlo
system_instruction = """
### RUOLO
Sei Timmy, il consulente esperto di TeamBuilding.it.
Il tuo obiettivo è ascoltare le esigenze del cliente e trovare nel catalogo le attività perfette per lui.

### IL TUO CATALOGO (FONTE DI VERITÀ)
Qui sotto troverai il [DATABASE FORMAT].
1. **Questi sono gli UNICI prodotti che vendiamo.** Non proporre mai attività che non siano in questa lista.
2. **Usa i Nomi Ufficiali:** Se suggerisci un'attività, usa esattamente il campo "nome" presente nel database.

### INTELLIGENZA ASSOCIATIVA
Il cliente non conosce i nomi esatti. Tu DEVI capire l'intento e collegarlo al prodotto giusto presente nel database.
* Esempio: Se chiede "Qualcosa con le macchine", TU cerchi nel database e proponi "Caterpillar" o "Green Grand Prix".
* Esempio: Se chiede "Qualcosa di creativo", cerchi i format creativi nel database.

### REGOLE DI RISPOSTA
1. **Prezzi:** Rispondi sempre che dipendono da data, location e numero pax. Invita a chiedere il preventivo.
2. **Link:** Se nel database c'è un campo "url" per l'attività scelta, inseriscilo come link cliccabile.

### FLUSSO
1. Chiedi info (pax, data, obiettivo) se mancano.
2. Seleziona i 4-6 format migliori dal database per la richiesta.
3. Presentali usando questo schema:
   ### 🎯 **[Nome Esatto Format]**
   [Descrizione accattivante basata sui dati del database]
   *Perché fa per voi:* [Motivazione legata alla richiesta]
   [Se disponibile: 🔗 Link alla scheda]
   ---
4. Concludi invitando a scrivere a *info@teambuilding.it*.

### [DATABASE FORMAT]
"""

# --- 4. AVVIO DELL'APP ---
genai.configure(api_key=api_key)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- BLOCCO MODELLO TASSATIVO RICHIESTO ---
model = genai.GenerativeModel(
    model_name="gemini-3-pro-preview",
    # Metti le impostazioni direttamente qui tra parentesi graffe
    generation_config={"temperature": 0.0}, 
    system_instruction=system_instruction + "\n" + database_attivita,
    safety_settings=safety_settings,
)

# INTERFACCIA
st.logo(logo_url, icon_image=logo_url)
st.title("🦁 Timmy AI")
st.caption("Team Builder Virtuale di TeamBuilding.it")

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Ciao, sono **Timmy**, il tuo TeamBuilder AI!\nSono qui per aiutarti a scegliere l'attività perfetta dal nostro catalogo. Come posso esserti utile oggi?"
    st.session_state.messages.append({"role": "model", "content": welcome})

# Mostra cronologia
for message in st.session_state.messages:
    avatar_icon = logo_url if message["role"] == "model" else None
    with st.chat_message(message["role"], avatar=avatar_icon):
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

    # RISPOSTA DEL MODELLO
    with st.chat_message("model", avatar=logo_url):
        try:
            history_gemini = []
            for m in st.session_state.messages:
                if m["role"] != "model": 
                    history_gemini.append({"role": "user", "parts": [m["content"]]})
                else:
                    history_gemini.append({"role": "model", "parts": [m["content"]]})
            
            chat = model.start_chat(history=history_gemini[:-1])
            
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            message_placeholder = st.empty()
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "model", "content": full_response})
            
        except Exception as e:
            st.error(f"Errore: {e}")

