
# esphomeGuieasy

![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Non-Commercial](https://img.shields.io/badge/Usage-Non--Commercial-red)
![Platform: PyQt6](https://img.shields.io/badge/UI-PyQt6-blue)
![Status: In Development](https://img.shields.io/badge/status-WIP-orange)

[![Donate](https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=HVA3DZFRLW9NU)

> 🇬🇧 If this project helped you, you can support the development via PayPal donation!

---

## 📝 Description

**esphomeGuieasy** is a Python desktop app with PyQt6 interface to simplify the creation, editing and flashing of ESPHome-compatible devices.

Designed for both beginners and power users, it features:
- YAML editor with syntax highlighting
- Integrated log console
- Drag-and-drop "brick" style sensor configuration
- Local and OTA flashing
- Board and template management

---

## 💾 Installation methods

### 🔹 Option 1: Using the Windows Installer (recommended for most users)

1. Download the `.exe` installer from the [Releases](https://github.com/YOUR_USERNAME/esphomeGuieasy/releases) page
2. Run the installer and follow the wizard
3. The program will be installed in `Program Files` and added to the Start menu and optionally the Desktop
4. On first launch, a folder will be created in your `Documents` for community projects and configuration

⚠️ **Security Notice:**  
Some antivirus (like Windows Defender) may **falsely flag the installer or `.exe` file** as a potential threat (e.g. *Phonzy.A!ml*).  
This is a **false positive**, due to the embedded Python environment and unsigned nature of the installer.  
You can safely allow it, or run the program directly from source.

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
git clone https://github.com/YOUR_USERNAME/esphomeGuieasy.git
cd esphomeGuieasy
```

#### 3. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate         # On Windows
# OR
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
core/       # YAML, flash, logging logic
gui/        # PyQt6 interface components
assets/     # Icons and graphics
config/     # Boards, templates
main.py     # Entry point
```

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
