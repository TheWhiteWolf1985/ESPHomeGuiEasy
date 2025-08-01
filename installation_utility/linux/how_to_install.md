# 🐧 How to Install ESPHomeGUIeasy on Linux

Welcome! This guide will walk you through installing and running **ESPHomeGUIeasy** on your Linux system.

---

## 🔹 Step-by-step installation

1. **Extract the archive**

   After downloading the `ESPHomeGUIeasy-linux.tar.gz` package, extract it to your preferred location:
   ```bash
   tar -xvzf ESPHomeGUIeasy-linux.tar.gz
   ```

2. **Run the installation script**

   Open a terminal in the extracted folder and run:
   ```bash
   ./install.sh
   ```

   This will:
   - Create user folders in your home (e.g. `~/ESPHomeGUIeasy/`)
   - Copy the configuration database (`user_config.db`) to `~/.config/ESPHomeGUIeasy/` if it doesn't exist
   - Copy the license folder (if present)

3. **Launch the interface**

   You can now start the app with:
   ```bash
   ./esphomeguieasy.sh
   ```

   Or double-click the file in your file manager (you may need to mark it as executable).

---

## 🛠️ Troubleshooting

- If nothing happens when double-clicking `.sh` files:
  - Right-click → Properties → Permissions → Enable "Allow executing as a program"
  - Or use the terminal:
    ```bash
    chmod +x filename.sh
    ```

- If serial ports are not detected:
  - Ensure your user is part of the `dialout` or `tty` group:
    ```bash
    sudo usermod -aG dialout $USER
    ```
  - Then reboot or log out and back in.

---

## 🧹 To remove the program

Simply delete the folder where you extracted `ESPHomeGUIeasy`, and optionally remove:

```bash
~/.config/ESPHomeGUIeasy/
~/ESPHomeGUIeasy/
```

---

## ✅ You're ready!

You can now start creating, editing and compiling ESPHome projects offline, directly from your Linux system 🚀
