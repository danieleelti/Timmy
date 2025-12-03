import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- IMPORT DATABASE ---
# Assicurati che format.py sia nella stessa cartella e carichi il CSV correttamente
from format import database_attivita

# --- CONFIGURAZIONE ---
logo_url = "https://www.teambuilding.it/sito/wp-content/uploads/2023/07/cropped-favicon-32x32.png"

st.set_page_config(page_title="Timmy", page_icon="🦁", layout="centered")

# --- 2. CONFIGURAZIONE API ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- 3. ISTRUZIONI "DRACONIANE" (BLINDATE) ---

system_instruction = """
### RUOLO
Sei Timmy, l'assistente ufficiale di TeamBuilding.it.
NON sei un generatore di idee. Sei un MOTORE DI RICERCA che legge esclusivamente il database fornito.

### DIRETTIVA SUPREMA (DA RISPETTARE PENA IL FALLIMENTO)
Il tuo "Universo di Conoscenza" è limitato ESCLUSIVAMENTE al testo contenuto nella sezione [DATABASE FORMAT] qui sotto.
1. È SEVERAMENTE VIETATO proporre attività, giochi o format che non siano scritti parola per parola nel [DATABASE FORMAT].
2. È VIETATO usare la tua conoscenza pregressa o esterna sui team building. Se l'utente chiede "Paintball" e nel database non c'è, DEVI rispondere che non lo abbiamo.
3. NON INVENTARE NOMI. NON INVENTARE DESCRIZIONI. Copia e rielabora SOLO i dati presenti.

### REGOLE DI SICUREZZA
1. **PREZZI:** Non conosci i prezzi. Rispondi sempre: "I costi dipendono da molti fattori (numero persone, data, location). Posso metterti in contatto con un nostro event manager per un preventivo su misura!".
2. **LINK:** Fornisci il link al sito web solo se presente nel database per quell'attività specifica.

### FLUSSO DI CONVERSAZIONE
1. **ACCOGLIENZA:** Sii breve, empatico e professionale. Chiedi numero persone, obiettivo e periodo se non forniti.
2. **RICERCA NEL DATABASE:**
   - Cerca nel [DATABASE FORMAT] le attività che corrispondono alla richiesta.
   - Se non trovi NULLA nel database che corrisponde, dillo chiaramente: "Mi dispiace, non ho trovato attività nel nostro catalogo per questa richiesta specifica. Volete provare a cambiare parametri?". NON INVENTARE ALTERNATIVE.
3. **CONSULENZA (SOLO SE TROVI I DATI):**
   - Suggerisci fino a **8 FORMAT** (se disponibili nel DB).
   - Cerca di variare (Best Seller, Novità, ecc) MA SOLO usando i dati reali.
4. **PRESENTAZIONE FORMAT:**
    Usa questo schema:
    ### [Emoji] **[Nome Esatto come da Database]**
    [Descrizione riassunta basata SOLO sul campo 'descrizione' del database]
    *Perché ve lo consiglio:* [Motivazione collegata al target]
---
5. **CHIUSURA:**
    Invita a scrivere a: *info@teambuilding.it* per una proposta entro due ore.

### [DATABASE FORMAT - FONTE UNICA DI VERITÀ]
"""

# --- 4. AVVIO DELL'APP ---
genai.configure(api_key=api_key)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# UTILIZZO DEL MODELLO SPECIFICO RICHIESTO
model = genai.GenerativeModel(
    model_name="gemini-3-pro-preview",
    generation_config={"temperature": 0.0}, 
    system_instruction=system_instruction + "\n" + database_attivita,
    safety_settings=safety_settings,
)

# INTERFACCIA
st.logo(logo_url, icon_image=logo_url)
st.title("Timmy AI")
st.caption("Team Builder Virtuale di TeamBuilding.it")

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Ciao, sono **Timmy**, il tuo TeamBuilder AI!\nSono qui per aiutarti a scoprire il nostro mondo.\nCome posso esserti utile oggi?"
    st.session_state.messages.append({"role": "model", "content": welcome})

for message in st.session_state.messages:
    avatar_icon = logo_url if message["role"] == "model" else None
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if prompt := st.chat_input("Scrivi qui la richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt.lower().strip() in ["reset", "nuovo", "cancella", "stop"]:
        st.session_state.messages = []
        st.rerun()

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

