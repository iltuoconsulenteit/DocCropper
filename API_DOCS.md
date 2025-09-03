# API Documentation

## Flussi di attivazione
- La chiave di licenza può essere specificata in `env/license.env`, in un file `.env` alla radice o in `settings.json`. La chiave definisce l'edizione attiva e può innescare convalide manuali oppure online in base al prefisso utilizzato.
- Le edizioni Pro e Full possono funzionare offline dopo l'attivazione; è richiesta la connessione solo per attivare o rinnovare la licenza e per le licenze sponsorizzate che recuperano i contenuti da Internet.

## Tipologie di licenza
- **Free** – watermark applicato e massimo cinque immagini per progetto.
- **Pro** – nessun watermark e immagini illimitate; un plugin LAN può limitare gli utenti di rete a blocchi di cinque.
- **Full** – tutte le funzionalità abilitate inclusi i plugin opzionali e l'accesso LAN illimitato.
- **Demo Full** – modalità nascosta con tutte le funzionalità ma con watermark e avvisi di demo.
- **Developer** – l'uso della chiave definita da `DOCROPPER_DEV_LICENSE` abilita funzionalità e plugin di sviluppo.
