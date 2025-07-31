# 🧩 How to Install ESPHomeGUIeasy on macOS

Follow these simple steps to install and run ESPHomeGUIeasy on your Mac.

---

## 📥 1. Download and Extract

1. Download the file `ESPHomeGUIeasy-macos.tar.gz` from the official release page.
2. Move it to your Desktop (or another convenient location).
3. Double-click the file to extract its contents. A new folder will appear.

---

## ⚙️ 2. Run the Installer

1. Open the extracted folder.
2. **Right-click** on the file `install.command`  
   → Select **Open** (the first time, you may need to confirm it's safe to run).
3. A terminal window will appear and the installation will begin.
4. Once finished, the app will launch automatically.

> 🧠 If the system shows a warning like “Unidentified Developer”, right-click again and select **Open** to bypass it.

---

## 🖥️ 3. What Happens During Installation?

- The app will be copied to your `Documents/ESPHomeGUIeasy/` folder.
- Required folders will be created: `build`, `user_projects`, etc.
- Python is embedded — no need to install anything.
- File permissions will be set automatically.

---

## 🧪 4. Troubleshooting

- **USB or Serial not detected?**  
  Go to **System Settings > Privacy & Security > Full Disk Access** and **USB Access**, then allow Terminal and the app.
  
- **The app doesn't start?**  
  Try launching manually from:  
  `Documents/ESPHomeGUIeasy/start.sh`

- **Permission errors?**  
  Re-run `install.command` or check that the files are not in a protected system folder.

---

## ✅ Done!

You are now ready to use ESPHomeGUIeasy on your Mac.  
Launch it from the Terminal, from `start.sh`, or create a shortcut.

---
