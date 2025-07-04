
# esphomeGuieasy

![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Non-Commercial](https://img.shields.io/badge/Usage-Non--Commercial-red)
![Platform: PyQt6](https://img.shields.io/badge/UI-PyQt6-blue)
![Status: In Development](https://img.shields.io/badge/status-WIP-orange)

[![Donate](https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=HVA3DZFRLW9NU)

> 🇬🇧 If this project helped you, you can support the development via PayPal donation!

---

📌 [Full changelog available here](CHANGELOG.md)

---
📝 Description

**ESPHomeGUIeasy** is a standalone desktop application written in Python with a modern PyQt6 interface, designed to simplify how you create, configure, and deploy firmware for **ESPHome-compatible devices** (ESP32, ESP8266, etc.).

It provides a full **visual workflow** — from device configuration to firmware flashing — with no need to write YAML manually (but you can if you want to).

Whether you're a beginner in home automation or a power user managing multiple devices, ESPHomeGUIeasy makes the process easier, faster, and more organized.

---

### 💡 Key Features

- 🧱 **Visual “block-style” editor**  
  Drag & drop preconfigured sensor/action blocks — no YAML syntax needed

- ✍️ **Live YAML preview & editing**  
  The interface updates YAML as you go — and you can still tweak it manually

- 🖥️ **Cross-platform UI**  
  Clean and responsive PyQt6-based GUI, available in multiple languages (EN, IT, ES, DE)

- 📄 **Project Manager** *(new in v1.4.0)*  
  Organize projects by category with metadata, changelogs, and quick actions

- 🔌 **Integrated Flashing**  
  Supports USB and OTA uploads with built-in log viewer

- 🧰 **Console with build logs**  
  Real-time output while building and flashing firmware

- 💾 **No external setup required**  
  Works out of the box — no need to install Python or ESPHome manually

---

**ESPHomeGUIeasy is open source** and intended for users who prefer a desktop-first approach to ESPHome development, especially when dealing with multiple devices or structured project folders.

---

## 💾 Installation methods

### 🔹 Option 1: Using the Windows Installer (recommended)

1. Download the `.exe` installer from the [Releases](https://github.com/YOUR_USERNAME/esphomeGuieasy/releases) page
2. Run the installer and follow the wizard
3. The program will be installed in `Program Files` and added to the Start menu and Desktop
4. On first launch:
   - You will be prompted to select a language
   - A user configuration database will be created in:
     `%APPDATA%\ESPHomeGUIeasy\user_config.db`
   - A log file will be created at:
     `%APPDATA%\ESPHomeGUIeasy\esphomeguieasy_log.txt`

⚠️ **Security Notice:**  
Some antivirus (like Windows Defender) may **falsely flag** the installer or `.exe` (e.g. *Phonzy.A!ml*).  
This is a **false positive**, due to the unsigned nature and embedded Python runtime.  
You can safely click **"More info → Run anyway"** when prompted by SmartScreen.

---

## 🖼 Screenshots

#### 🏠 Main Interface
![Main Interface](docs/images/screenshot_main.png)

#### 🧱 Sensor Configuration (Bricks)
![Sensor Configuration](docs/images/screenshot_sensors.png)

#### ⚙️ Compilation and Upload
![Compilation and Upload](docs/images/screenshot_compile.png)

#### 🔧 Settings Panel
![Settings](docs/images/screenshot_settings.png)


---

### 🔹 Option 2: Running from source

#### 1. Prerequisites
- Python **3.10 or higher** ([download here](https://www.python.org/downloads/))
- [ESPHome](https://esphome.io/) globally installed:
  ```bash
  pip install esphome
  ```
- OS: **Windows, Linux, macOS**

#### 2. Clone the repository
```bash
git clone https://github.com/TheWhiteWolf1985/ESPHomeGuiEasy.git
cd esphomeGuieasy
```

#### 3. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate         # On Windows
# OR
python -m venv venv
source venv/bin/activate      # On macOS/Linux
```

#### 4. Install dependencies
```bash
pip install -r requirements.txt
```

#### 5. Run the app
```bash
python main.py
```

---

## 🧰 Dependencies

- **PyQt6** — graphical interface
- **ruamel.yaml** — YAML handling
- **pyserial** — serial port communication

---

## 🛠 Troubleshooting

- **ModuleNotFoundError: 'PyQt6'**
  - Make sure you activated the `venv` before installing requirements
  - Try: `pip install -r requirements.txt`

- **'esphome' not found**
  - Ensure it's installed globally via `pip install esphome`

- **Permission error on serial ports (Linux/macOS):**
  ```bash
  sudo usermod -aG dialout $(whoami)
  ```

- **Unexpected error or crash**
  - Open an issue and provide:
    - OS and version
    - Python version
    - Full error log

---

## 📁 Project Structure

```
core/ # YAML, flash, logging logic
gui/ # PyQt6 interface components
assets/ # Icons and graphics
config/ # Boards, templates
main.py # Entry point (called from ESPHomeRunner.exe or .bat)
```

---

## 🗂️ Where user files are stored

After installation, the application creates the following directory for configuration and logs:

%APPDATA%\ESPHomeGUIeasy\

- `user_config.db` — contains language and startup preferences
- `esphomeguieasy_log.txt` — contains startup logs and crash info

This folder is fully writable by the user. You can delete it to reset the application to first-launch state.


---

## 📜 License

**AGPL v3 with additional terms** – see [LICENSE.txt](./LICENSE.txt)

> ⚠️ This project is released for **personal, educational, and non-commercial use only**.  
> **Commercial use is strictly prohibited** without prior written permission from the author.

---

## 🤝 Contributing

Contributions are welcome via pull request or issue.  
Please report bugs in the [Issues section](https://github.com/YOUR_USERNAME/esphomeGuieasy/issues) with:
- OS and version
- Python version
- Steps to reproduce the problem
