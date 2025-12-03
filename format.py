import csv
import json
import os

def carica_database():
    # Il nome esatto del tuo file su GitHub
    nome_file = 'MasterTimmy.csv'
    
    lista_prodotti = []
    
    # 1. Controllo se il file esiste (per evitare crash brutti)
    if not os.path.exists(nome_file):
        messaggio_errore = (
            f"ATTENZIONE: Il file '{nome_file}' non è stato trovato nella cartella principale. "
            "Caricalo su GitHub accanto ad app.py."
        )
        return messaggio_errore

    try:
        # 2. Apertura e lettura del CSV
        with open(nome_file, mode='r', encoding='utf-8') as file:
            # DictReader usa la prima riga (intestazioni) come chiavi
            # Assicurati che il tuo CSV abbia le intestazioni: nome, format, logistica, ecc.
            reader = csv.DictReader(file)
            
            for row in reader:
                # Pulizia opzionale: rimuove righe vuote se ce ne sono
                if row.get('nome'): 
                    lista_prodotti.append(row)
        
        # 3. Conversione in testo JSON per l'AI
        # ensure_ascii=False serve per mantenere accenti e caratteri speciali italiani
        database_stringa = json.dumps(lista_prodotti, indent=2, ensure_ascii=False)
        return database_stringa

    except Exception as e:
        return f"ERRORE CRITICO nella lettura di {nome_file}: {e}"

# --- ESECUZIONE ---
# Quando app.py fa "from format import database_attivita",
# questa funzione parte in automatico e carica i dati aggiornati.
database_attivita = carica_database()
