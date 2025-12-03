import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import google.generativeai as genai
import json
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
# ... (Blocco DEBUG omesso per brevità) ...
# --- FINE BLOCCO DEBUG ---

# --- 2. CONFIGURAZIONE API ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

# --- FUNZIONE DI INVIO EMAIL (FIXED + UX) ---

def send_chat_via_email(recipient_email, chat_history):
    try:
        sender_email = st.secrets["smtp"]["sender_email"]
        sender_password = st.secrets["smtp"]["sender_password"]
        smtp_server = st.secrets["smtp"]["host"] 
        smtp_port = int(st.secrets["smtp"]["port"]) 
    except KeyError:
        st.error("❌ Si è verificato un errore interno. Riprova più tardi.") 
        return False

    destinatari = [recipient_email, EMAIL_COMMERCIALE]
    
    try:
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

        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, destinatari, msg.as_string()) 
            
        st.success(f"✅ Email di consulenza inviata a {recipient_email} e a {EMAIL_COMMERCIALE}!")
        return True

    except smtplib.SMTPAuthenticationError:
        st.error("❌ Non siamo riusciti ad autenticarci. Contatta il supporto tecnico.")
        return False
    except smtplib.SMTPConnectError:
        st.error("❌ Errore di connessione. Il server di posta non è raggiungibile.")
        return False
    except Exception:
        st.error("❌ Errore critico di invio. Riprova o contatta il supporto.")
        return False
# --- FINE FUNZIONE EMAIL FIXED + UX ---

# --- 3. ISTRUZIONI DI SISTEMA ---
# ... (Blocco ISTRUZIONI omesso per brevità) ...
system_instruction = """
### RUOLO
Sei Timmy, il consulente esperto di TeamBuilding.it.
... (Omissis ISTRUZIONI) ...
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

# -------------------------------------------------------------------------------------
# --- NUOVO ORDINE UX: 1. Form Commerciale | 2. Linea di Separazione | 3. Input Prompt ---
# -------------------------------------------------------------------------------------

# Linea di separazione per estetica (SOPRA IL FORM)
st.divider() 

# Condizione: mostriamo il form solo se ci sono almeno due messaggi
if len(st.session_state.messages) >= 2:
    with st.form("email_form", clear_on_submit=True):
        st.markdown("### 💌 Richiedi una Proposta Commerciale")
        st.markdown("Inserisci la tua email per ricevere subito il riepilogo della consulenza e una proposta ad-hoc entro due ore.")
        
        user_email = st.text_input("La tua email:", key="user_email_input")
        
        submitted = st.form_submit_button("Invia cronologia e richiedi preventivo")
        
        # LOGICA DEL FORM (DEVE RESTARE QUI DENTRO!)
        if submitted and user_email:
            # Validazione base dell'email
            if "@" not in user_email or "." not in user_email:
                st.warning("Per favore, inserisci un indirizzo email valido.")
            else:
                success = send_chat_via_email(user_email, st.session_state.messages)

                if success:
                    st.success(f"✅ Richiesta inviata! Il riepilogo è stato spedito a {user_email}. Sarai ricontattato prestissimo.")
                    st.markdown("---")
                    st.info("👉 Grazie di averci scritto! Verrai ricontattato a breve dal nostro team commerciale.")
            
        elif submitted and not user_email:
            st.warning("Inserisci l'email per procedere.")

# --- NUOVO ORDINE UX: 2. Input Prompt (ultima istruzione UI) ---
# La logica del prompt e della risposta Gemini deve restare qui per funzionare correttamente
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
