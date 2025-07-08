# esphomeGuieasy

![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Non-Commercial](https://img.shields.io/badge/Usage-Non--Commercial-red)
![Platform: PyQt6](https://img.shields.io/badge/UI-PyQt6-blue)
![Status: In Development](https://img.shields.io/badge/status-WIP-orange)

[![Donate](https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=HVA3DZFRLW9NU)

> If this project helped you, you can support the development via PayPal donation!

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

- 📄 **Project Manager** *(since v1.4.0)*  
  Organize projects by category with metadata, changelogs, and quick actions

- 🔌 **Integrated Flashing**  
  Supports USB and OTA uploads with built-in log viewer

- 🧰 **Console with build logs**  
  Real-time output while building and flashing firmware

- 📁 **Local project folder & YAML structure**  
  Compatible with ESPHome CLI structure

- 💾 **Works out of the box**  
  No Python installation or venv required — ships with Python embedded

---

**ESPHomeGUIeasy is open source** and intended for users who prefer a desktop-first approach to ESPHome development, especially when dealing with multiple devices or structured project folders.

---

## 📚 Technical Documentation

- \ref boards "📦 Supported Boards"
- \ref modules_schema "🧱 Modules Schema"
- \ref sensors "🌡 Sensor Definitions"


---

## 💾 Installation

### 🔹 Option 1: Using the Windows Installer (recommended)

1. Download the `.exe` installer from the [Releases](https://github.com/YOUR_USERNAME/esphomeGuieasy/releases) page
2. Run the installer and follow the wizard
3. The program will be installed in `Program Files` and added to the Start menu and Desktop
4. On first launch:
   - You will be prompted to select a language
   - A user configuration database will be created in:
     `%LOCALAPPDATA%\ESPHomeGUIeasy\user_config.db`
   - A log file will be created at:
     `%LOCALAPPDATA%\ESPHomeGUIeasy\esphomeguieasy_log.txt`

⚠️ **Security Notice:**  
Some antivirus (like Windows Defender) may **falsely flag** the installer or `.exe` (e.g. *Phonzy.A!ml*).  
This is a **false positive**, due to the unsigned nature and embedded Python runtime.  
You can safely click **"More info → Run anyway"** when prompted by SmartScreen.

---

## 🖼 Screenshots

#### 🏠 Main Interface
![Main Interface](images/screenshot_main.png)

#### 🧱 Sensor Configuration (Bricks)
![Sensor Configuration](images/screenshot_sensors.png)

#### ⚙️ Compilation and Upload
![Compilation and Upload](images/screenshot_compile.png)

#### 🔧 Settings Panel
![Settings](images/screenshot_settings.png)

---

## 🧰 Dependencies (already bundled in embedded build)

- **PyQt6** — graphical interface
- **ruamel.yaml** — YAML handling
- **pyserial** — serial port communication

---

## 🛠 Troubleshooting

- **The program doesn't start**
  - Check that it was extracted correctly and not blocked by antivirus
  - Run from terminal to capture output: `ESPHomeGUIeasy.exe > log.txt 2>&1`

- **'esphome' not found**
  - Ensure `esphome` is installed and available in PATH
  - Or use the internal ESPHome bundled with the GUI

- **Permission error on serial ports (Linux/macOS):**
  ```bash
  sudo usermod -aG dialout $(whoami)
  ```

---

## 📁 Project Structure

```
core/        # YAML management, flashing, logging
gui/         # GUI interface (PyQt6)
config/      # JSON templates for boards, sensors, modules
docs/        # Doxygen-generated documentation
main.py      # Main application entry point
```

---

## 🗂️ Where user files are stored

After installation, the application creates the following directory:

`%LOCALAPPDATA%\ESPHomeGUIeasy\`

- `user_config.db` — configuration and language settings
- `esphomeguieasy_log.txt` — full session log

This folder is fully writable and persistent between runs. Delete it to reset the app.

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