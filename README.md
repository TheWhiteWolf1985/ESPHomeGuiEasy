# esphomeGuieasy

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform: PyQt6](https://img.shields.io/badge/UI-PyQt6-blue)
![Status: In Development](https://img.shields.io/badge/status-WIP-orange)

**esphomeGuieasy** è un'applicazione desktop in Python con interfaccia PyQt6 progettata per semplificare la creazione, la configurazione e il flashing dei dispositivi compatibili con ESPHome.  
Pensata per neofiti e utenti esperti, fornisce:

- Interfaccia YAML editor avanzata con evidenziazione sintassi
- Console interattiva per log e operazioni
- Sistema a "mattoncini" per configurare sensori graficamente
- Flash locale e OTA, gestione board, caricamento template

## 🛠️ Requisiti

- Python 3.10+
- PyQt6
- ESPHome (installato nel sistema)

## 📁 Struttura

```
core/               # Gestione YAML, log, flashing
gui/                # Interfaccia PyQt6
assets/             # Icone, immagini pinout
config/             # Template YAML, lista board
main.py             # Entry point
```

## 📄 Licenza

Rilasciato sotto licenza MIT - vedi [LICENSE](./LICENSE)

---

Contribuzioni benvenute!
