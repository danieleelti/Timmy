import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import google.generativeai as genai
import json
import time 
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- IMPORT DATABASE ---
# Assicurati che il file format.py sia nella stessa cartella
from format import database_attivita
from faq import faq_database      
from location import location_database  

# --- CONFIGURAZIONE ---
# Indirizzo del team commerciale che riceverà la notifica
EMAIL_COMMERCIALE = "info@teambuilding.it"  
logo_url = "https://www.teambuilding.it/sito/wp-content/uploads/2023/07/cropped-favicon-32x32.png"

st.set_page_config(page_title="Timmy", page_icon="🦁", layout="centered")

# --- DEBUG LATERALE (Verifica caricamento di TUTTI i database) ---
# Per nascondere le scritte, basta commentare l'intero blocco (con #)
# try:
    # 1. FORMAT DB
  # format_count = len(json.loads(database_attivita))
  # st.sidebar.success(f"✅ Catalogo FORMAT: {format_count} voci.")
    
    # 2. FAQ DB
  # faq_count = len(json.loads(faq_database))
  # st.sidebar.success(f"✅ Catalogo FAQ: {faq_count} voci.")
    
    # 3. LOCATION DB
  # location_count = len(json.loads(location_database))
  # st.sidebar.success(f"✅ Catalogo LOCATION: {location_count} voci.")

# except Exception as e:
   # st.sidebar.error("❌ ERRORE CRITICO di caricamento DB.")
   # st.sidebar.exception(e) # Puoi decommentare questa riga per vedere l'errore esatto

# --- FINE BLOCCO DEBUG ---

# --- 2. CONFIGURAZIONE API ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- FUNZIONE DI INVIO EMAIL (NESSUN MESSAGGIO DI DEBUG) ---

def send_chat_via_email(recipient_email, chat_history):
    try:
        sender_email = st.secrets["smtp"]["sender_email"]
        sender_password = st.secrets["smtp"]["sender_password"]
        smtp_server = st.secrets["smtp"]["host"] 
        smtp_port = int(st.secrets["smtp"]["port"]) 
    except KeyError:
        # L'errore non viene stampato, la funzione restituisce False
        return False

    # Definiamo la lista dei destinatari finali
    destinatari = [recipient_email, EMAIL_COMMERCIALE]
    
    try:
        # Crea il corpo dell'email (omesso per brevità)
        body = "Ecco la cronologia della conversazione con Timmy AI:\n\n"
        for message in chat_history:
            role = "UTENTE" if message["role"] == "user" else "TIMMY AI"
            content = message['content'].replace('**', '').replace('###', '').replace('\n', '\n')
            body += f"--- {role} ---\n{content}\n\n"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Cc'] = EMAIL_COMMERCIALE
        msg['Subject'] = f"Consulenza Timmy AI per {recipient_email} - TeamBuilding.it"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # TENTATIVO DI INVIO
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, destinatari, msg.as_string()) 
            
        # *** RIMOSSA st.success QUI ***
        return True

    except smtplib.SMTPAuthenticationError:
        return False
    except smtplib.SMTPConnectError:
        return False
    except Exception:
        return False
# --- FINE FUNZIONE EMAIL (NESSUN MESSAGGIO DI DEBUG) ---

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

# --- BLOCCO MODELLO TASSATIVO RICHIESTO (con TUTTI i Database) ---

# 1. Creiamo la stringa completa del prompt unendo ISTRUZIONI + tutti i DATASET
full_prompt_with_data = (
    system_instruction + 
    "\n\n### [FAQ AZIENDALI]:\n" + faq_database + 
    "\n\n### [COPERTURA GEOGRAFICA]:\n" + location_database +
    "\n\n### [DATABASE FORMAT]:\n" + database_attivita
)

model = genai.GenerativeModel(
    model_name="gemini-3-pro-preview",
    generation_config={"temperature": 0.0}, 
    system_instruction=full_prompt_with_data,
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

# --- ZONA DI INPUT E FORM (Posizionamento Standard) ---

# --- 1. Input Prompt (Attiva la Logica di Rerunning) ---
if prompt := st.chat_input("Scrivi qui la richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun() 

# --- 2. LOGICA DI RISPOSTA GEMINI (CON SPINNER CIRCOLARE) ---

# Controlliamo l'ultimo messaggio inviato per la logica di generazione
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    # Reset
    if current_prompt.lower().strip() in ["reset", "nuovo", "cancella", "stop"]:
        st.session_state.messages = []
        st.rerun()

    # ⭐ SPINNER CIRCOLARE (st.spinner)
    with st.spinner("🧠 Timmy AI sta elaborando la tua richiesta..."):
        
        # RISPOSTA DEL MODELLO
        with st.chat_message("model", avatar=logo_url):
            try:
                history_gemini = []
                # Tutta la cronologia tranne l'ultimo (il prompt corrente)
                for m in st.session_state.messages[:-1]: 
                    history_gemini.append({"role": m["role"], "parts": [m["content"]]})
                
                # Inizio della generazione
                chat = model.start_chat(history=history_gemini)
                response = chat.send_message(current_prompt, stream=True)
                
                full_response = ""
                message_placeholder = st.empty()
                
                # Streaming della risposta
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Aggiungiamo la risposta completa solo alla fine
                st.session_state.messages.append({"role": "model", "content": full_response})
                
                # Lo spinner si chiude automaticamente all'uscita dal blocco 'with st.spinner'

            except Exception as e:
                st.error(f"❌ Errore durante la generazione della risposta: {e}")


# ----------------------------------------------------------------------
# --- 3. FORM COMMERCIALE (DOPO LA RISPOSTA) ---
# ----------------------------------------------------------------------

# Linea di separazione per estetica
st.divider() 

# Condizione: mostriamo il form solo se ci sono almeno due messaggi
if len(st.session_state.messages) >= 2:
    
    # IL FORM DEVE CONTENERE TUTTA LA SUA LOGICA
    with st.form("email_form", clear_on_submit=True):
        st.markdown("### 💌 Richiedi una Proposta Commerciale")
        st.markdown("Inserisci la tua email per ricevere subito il riepilogo della consulenza e una proposta ad-hoc entro due ore.")
        
        user_email = st.text_input("La tua email:", key="user_email_input")
        
        submitted = st.form_submit_button("Invia cronologia e richiedi preventivo")
        
        # LOGICA CORRETTA: TUTTO IL CONTROLLO 'if submitted' è all'interno del form
        if submitted and user_email:
            # Validazione base dell'email
            if "@" not in user_email or "." not in user_email:
                st.warning("Per favore, inserisci un indirizzo email valido.")
            else:
                success = send_chat_via_email(user_email, st.session_state.messages)

                # Mostra il ringraziamento finale (blu) SOLO se l'invio è andato a buon fine
                if success:
                    # *** RIMOSSA st.success qui, mantenendo solo il messaggio blu in fondo ***
                    st.markdown("---")
                    st.info("👉 Grazie di averci scritto! Verrai ricontattato a breve dal nostro team commerciale.")
            
        elif submitted and not user_email:
            st.warning("Inserisci l'email per procedere.")
