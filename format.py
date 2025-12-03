import csv
import json
import os

def carica_database_da_csv():
    # Nome del file che hai caricato su GitHub
    nome_file = 'MasterTimmy.csv'
    
    lista_prodotti = []
    
    # Controlliamo se il file esiste
    if not os.path.exists(nome_file):
        return "ERRORE: Il file CSV non è stato trovato. Caricalo su GitHub con il nome 'MasterTimmy.csv'."

    try:
        with open(nome_file, mode='r', encoding='utf-8') as file:
            # DictReader converte automaticamente ogni riga in un dizionario usando le intestazioni
            reader = csv.DictReader(file)
            for row in reader:
                # Pulizia: convertiamo True/False testuali in booleani reali se necessario
                # (Opzionale, ma aiuta l'AI)
                if 'social_activity' in row:
                    if row['social_activity'].lower() in ['sì', 'si', 'true', 'yes', 'sino']:
                        row['social_activity'] = True
                    else:
                        row['social_activity'] = False
                
                lista_prodotti.append(row)
        
        # Convertiamo la lista in una stringa JSON formattata per l'AI
        database_stringa = json.dumps(lista_prodotti, indent=2, ensure_ascii=False)
        return database_stringa

    except Exception as e:
        return f"ERRORE nella lettura del CSV: {e}"

# Questa è la variabile che app.py importerà
database_attivita = carica_database_da_csv()
