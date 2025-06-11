# esphomeGuieasy

![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Non-Commercial](https://img.shields.io/badge/Usage-Non--Commercial-red)
![Platform: PyQt6](https://img.shields.io/badge/UI-PyQt6-blue)
![Status: In Development](https://img.shields.io/badge/status-WIP-orange)


[![Donate](https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=HVA3DZFRLW9NU)

> 🇮🇹 Se questo progetto ti è stato utile, puoi supportare lo sviluppo con una donazione PayPal!
> 🇬🇧 If this project helped you, you can support the development via PayPal donation!

---

## 🇬🇧 Description

**esphomeGuieasy** is a Python desktop app with PyQt6 interface to simplify the creation, editing and flashing of ESPHome-compatible devices.
Designed for both beginners and power users, it features:
- YAML editor with syntax highlighting
- Integrated log console
- Drag-and-drop "brick" style sensor configuration
- Local and OTA flashing, board management, template loader

---

## 🇬🇧 Step-by-step Installation

### 1. Prerequisites
- Python **3.10 or higher** ([download here](https://www.python.org/downloads/))
- [ESPHome](https://esphome.io/) globally installed:
  ```bash
  pip install esphome
  ```
- Operating System: **Windows, Linux, macOS**

### 2. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/esphomeGuieasy.git
cd esphomeGuieasy
```

### 3. Create a virtual environment (optional but recommended)
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
**Windows:**
```cmd
pip install -r requirements.txt
```
**macOS / Linux:**
```bash
pip3 install -r requirements.txt
```

### 5. Run the application
**Windows:**
```cmd
python main.py
```
**macOS / Linux:**
```bash
python3 main.py
```

#### Main dependencies
- **PyQt6** — GUI
- **ruamel.yaml** — YAML handling
- **pyserial** — Serial port support

---

### 🚑 Troubleshooting (EN)

- **Error: "ModuleNotFoundError: No module named 'PyQt6'"**  
  ➔ Make sure you have activated the virtualenv **before** installing requirements and running the program.  
  ➔ Try reinstalling: `pip install -r requirements.txt`

- **Error: "esphome not found"**  
  ➔ Make sure you installed ESPHome globally with `pip install esphome` (you may need `pip3` on Linux/macOS).  
  ➔ Check that your PATH environment variable is updated.

- **Serial port permission error (Linux/macOS):**  
  ➔ Add your user to the `dialout` group (Linux):
  ```bash
  sudo usermod -aG dialout $(whoami)
  ```
  ➔ After this, log out and back in.

- **Unexpected crash or bug:**  
  ➔ Open an Issue in the [Bug](https://github.com/YOUR_USERNAME/esphomeGuieasy/issues) section and provide:
    - Operating system and version
    - Python version (`python --version`)
    - Version of esphome, PyQt6, ruamel.yaml
    - Full error log

---

## 🇮🇹 Descrizione

**esphomeGuieasy** è un'app desktop Python con interfaccia PyQt6 per facilitare la creazione, la modifica e il flashing di dispositivi compatibili ESPHome.
Pensata sia per neofiti che utenti esperti, offre:
- Editor YAML con evidenziazione della sintassi
- Console log integrata
- "Mattoncini" grafici per configurare sensori
- Flash locale e OTA, gestione board, caricamento template

---

## 🇮🇹 Installazione passo-passo

### 1. Prerequisiti
- Python **3.10 o superiore** ([scarica qui](https://www.python.org/downloads/))
- [ESPHome](https://esphome.io/) installato globalmente:
  ```bash
  pip install esphome
  ```
- Sistema operativo: **Windows, Linux, macOS**

### 2. Clona il repository
```bash
git clone https://github.com/TUO_USERNAME/esphomeGuieasy.git
cd esphomeGuieasy
```

### 3. Crea un ambiente virtuale (opzionale ma consigliato)
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Installa le dipendenze
**Windows:**
```cmd
pip install -r requirements.txt
```
**macOS / Linux:**
```bash
pip3 install -r requirements.txt
```

### 5. Avvia l’applicazione
**Windows:**
```cmd
python main.py
```
**macOS / Linux:**
```bash
python3 main.py
```

#### Dipendenze principali
- **PyQt6** — GUI
- **ruamel.yaml** — Gestione YAML
- **pyserial** — Supporto seriale

---

### 🚑 Troubleshooting (IT)

- **Errore: "ModuleNotFoundError: No module named 'PyQt6'"**  
  ➔ Verifica di aver attivato il virtualenv **prima** di installare le dipendenze e di avviare il programma.  
  ➔ Prova a reinstallare: `pip install -r requirements.txt`

- **Errore: "esphome non trovato"**  
  ➔ Assicurati di aver installato ESPHome globalmente con `pip install esphome` (potresti dover usare `pip3` su Linux/macOS).  
  ➔ Controlla di avere la variabile d'ambiente PATH aggiornata.

- **Errore di permessi sulla porta seriale (Linux/macOS):**  
  ➔ Aggiungi il tuo utente al gruppo `dialout` (Linux):
  ```bash
  sudo usermod -aG dialout $(whoami)
  ```
  ➔ Dopo il comando, esegui logout/login.

- **Crash o bug non previsti:**  
  ➔ Apri una Issue nella sezione [Bug](https://github.com/TUO_USERNAME/esphomeGuieasy/issues) riportando:
    - Sistema operativo e versione
    - Versione di Python (`python --version`)
    - Versione di esphome, PyQt6, ruamel.yaml
    - Log completo dell’errore

---

## 📁 Struttura / Structure

```
core/       # YAML, log, flash handling
gui/        # PyQt6 UI
assets/     # Icons, pinout images
config/     # YAML templates, board list
main.py     # Entry point
```

## 📄 License

**AGPL v3 with additional terms** – see [LICENSE.txt](./LICENSE.txt)

> ⚠️ This project is released for **personal, educational, and non-commercial use only**.  
> **Commercial use is strictly prohibited** without prior written permission from the author.  
> For commercial licensing, please contact the author.

---

**AGPL v3 con termini aggiuntivi** – vedi [LICENSE.txt](./LICENSE.txt)

> ⚠️ Questo progetto è rilasciato per **uso personale, educativo e non commerciale**.  
> **L'uso commerciale è severamente vietato** senza autorizzazione scritta dell'autore.  
> Per licenze commerciali, contattare l'autore.



---

## 🙌 Contribuire / Contributing

Le contribuzioni sono benvenute tramite issue o pull request.  
Contributions are welcome via issues or pull requests.

Ogni errore riscontrato va segnalato nella sezione "Bug" del repository per garantire il tracciamento e la risoluzione.  
All errors must be reported in the "Bug" section of the repository to ensure tracking and resolution.

---
