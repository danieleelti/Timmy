import csv
import json
import os

def carica_database():
    nome_file = 'MasterTimmy.csv'
    lista_prodotti = []
    
    if not os.path.exists(nome_file):
        return json.dumps([{"nome": "ERRORE", "descrizione": "File CSV non trovato su GitHub."}])

    # Definiamo gli encoding da provare
    encoding_list = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encoding_list:
        try:
            with open(nome_file, mode='r', encoding=encoding, errors='replace') as file:
                # 1. Tenta di rilevare il separatore
                prima_riga = file.readline()
                file.seek(0)
                separatore = ';' if ';' in prima_riga else ','
                
                reader = csv.DictReader(file, delimiter=separatore)
                
                for row in reader:
                    if row.get('Nome Format') or row.get('Nome'): # Usiamo la chiave corretta
                        row_clean = {}
                        
                        for k, v in row.items():
                            if k:
                                # 2. Pulizia e conversione chiave/valore
                                key = k.strip().lower().replace(' ', '_')
                                value = v.strip() if v else ""
                                
                                # 3. CORREZIONE VIRGOLA DECIMALE (Importante se non hai aggiornato il CSV!)
                                if 'durata' in key or 'pax' in key or 'ranking' in key:
                                    value = value.replace(',', '.') # Sostituisce la virgola decimale con il punto
                                    
                                row_clean[key] = value
                                
                        lista_prodotti.append(row_clean)
                
                # Se arriviamo qui, il file è stato letto
                database_stringa = json.dumps(lista_prodotti, indent=2, ensure_ascii=False)
                return database_stringa

        except UnicodeDecodeError:
            continue
        except Exception as e:
            # Se fallisce per un errore di struttura, proviamo il prossimo encoding
            continue

    # Se fallisce tutto, restituisce un errore chiaro all'AI
    return json.dumps([{"nome": "ERRORE FINALE", "descrizione": "Impossibile leggere il catalogo MasterTimmy. Controlla il formato CSV e la codifica."}])

# ESECUZIONE
database_attivita = carica_database()
