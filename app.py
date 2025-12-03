import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- IMPORT DATABASE ---
from format import database_attivita

# --- CONFIGURAZIONE ---
# 1. URL DEL LOGO (Lo definiamo qui per comodità)
logo_url = "https://www.teambuilding.it/sito/wp-content/uploads/2023/07/cropped-favicon-32x32.png"

# 2. CONFIGURAZIONE PAGINA
# Nota: page_icon accetta solo Emoji o file locali. Lasciamo il leone per il browser tab,
# oppure carica il file 'logo.png' su GitHub e scrivi page_icon="logo.png"
st.set_page_config(page_title="Timmy", page_icon="🦁", layout="centered")

# --- 2. CONFIGURAZIONE API ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- 3. DEFINIZIONE PROMPT E DATABASE ---

system_instruction = """
### SEI L'ASSISTENTE VIRTUALE UFFICIALE DI TEAMBUILDING.IT.
Il tuo obiettivo è aiutare i visitatori a trovare l'attività perfetta e invogliarli a chiedere un preventivo al nostro staff umano.

### REGOLE DI SICUREZZA (TASSATIVE)
1. **NON PARLARE MAI DI PREZZI:** Tu non conosci i prezzi. Se ti chiedono "Quanto costa?", rispondi: "I costi dipendono da molti fattori (numero persone, data, location). Posso metterti in contatto con un nostro event manager per un preventivo su misura!".
2. **NON INVENTARE:** Usa SOLO i format elencati nel [DATABASE FORMAT] qui sotto. Se un format non c'è, di' che non è disponibile.
3. **LINK:** Su richiesta fornisci il link al sito web 

### FLUSSO DI CONVERSAZIONE
1. **ACCOGLIENZA:** Sii, empatico e professionale. Ciao sono Timmy, come posso aiutarti? avete già delle idee in mente per il vostro evento? In seconda battuta chiedi numero persone, obiettivo, periodo.
2. **CONSULENZA:** In base alle risposte, suggerisci **8 FORMAT** che siano perfetti per loro:
    * 2 Best Seller
    * 2 Novità
    * 2 Vibe (Mood adatto)
    * 2 Social
3. **PRESENTAZIONE FORMAT:**
    Usa questo schema per ogni suggerimento:
    ### [Emoji a tua scelta attinente al format] **[Nome Format]**
    [Breve descrizione accattivante basata sulla colonna Descrizione]
    *Perché ve lo consiglio:* [Tua ampia motivazione legata alla loro richiesta]
---
4. **CHIUSURA (Call to Action):**
    Concludi sempre invitando a contattarci: *"Volete approfondire uno di questi o preferite altre idee? potete inviarci subito una mail a info@teambuilding.it, vi manderemo una proposta ad hoc entro due ore."*

### [DATABASE FORMAT - NO PREZZI]
"""

# --- 4. AVVIO DELL'APP ---
genai.configure(api_key=api_key)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config={"temperature": 0.0}, 
    system_instruction=system_instruction + "\n" + database_attivita,
    safety_settings=safety_settings,
)

# INTERFACCIA
# Usiamo il logo anche nel titolo tramite un trucco markdown (opzionale, ma carino)
st.logo(logo_url, icon_image=logo_url) # Appare in alto a sinistra nella sidebar se la apri
st.title("Timmy AI")
st.caption("Team Builder Virtuale di TeamBuilding.it")

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Ciao, sono **Timmy**, il tuo TeamBuilder AI!\nSono qui per aiutarti a scoprire il nostro mondo. Come posso esserti utile oggi?"
    st.session_state.messages.append({"role": "model", "content": welcome})

# Mostra cronologia
for message in st.session_state.messages:
    # Se il messaggio è dell'AI (model), usiamo il logo personalizzato come avatar
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
    # Anche qui usiamo il logo mentre scrive
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
