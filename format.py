import csv
import json
import os

def carica_database():
    # Nome del file (assicurati che su GitHub sia caricato nella stessa cartella!)
    nome_file = 'MasterTimmy.csv'
    
    lista_prodotti = []
    
    # 1. Verifica esistenza file
    if not os.path.exists(nome_file):
        # Fallback: prova a cercarlo tutto minuscolo se non lo trova
        if os.path.exists(nome_file.lower()):
            nome_file = nome_file.lower()
        else:
            return json.dumps([{"nome": "ERRORE", "descrizione": "File CSV non trovato su GitHub."}])

    try:
        # 2. Lettura intelligente (Rileva automaticamente il separatore)
        with open(nome_file, mode='r', encoding='utf-8', errors='replace') as file:
            # Leggiamo la prima riga per capire se usa , o ;
            prima_riga = file.readline()
            file.seek(0) # Torniamo all'inizio
            
            separatore = ';' if ';' in prima_riga else ','
            
            reader = csv.DictReader(file, delimiter=separatore)
            
            for row in reader:
                # Aggiungiamo solo se c'è almeno il nome del format
                if row.get('nome') or row.get('Nome') or row.get('NOME'):
                    # Normalizziamo le chiavi (tutto minuscolo) per sicurezza
                    row_clean = {k.lower(): v for k, v in row.items() if k}
                    lista_prodotti.append(row_clean)
        
        return json.dumps(lista_prodotti, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps([{"nome": "ERRORE LETTURA", "descrizione": str(e)}])

# ESECUZIONE
database_attivita = carica_database()
