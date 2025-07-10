# 📄 ESPHomeGUIeasy – Changelog

A complete list of changes for each released version of ESPHomeGUIeasy.  
All versions are listed in descending order, with the latest release at the top.

## 🔔 Version 1.4.1 – Maintenance + Enhancements

### 🧩 Enhancements

**• Improved stability and UX**
- The project manager now handles missing or malformed metadata more gracefully.
- Labels and tooltips revised for better clarity in multilingual setups.

**• Offline documentation viewer**
- Doxygen-generated HTML documentation is now included and accessible via the Help menu.
- Available even without internet connection.

**• Uninstall shortcut and version description**
- A Start menu shortcut has been added to allow quick access to uninstallation.
- The installer now shows a localized description during setup.

**• Menu refinements**
- Help menu expanded with access to About and Documentation entries.
- File and Settings menus optimized for readability and logic.

### 🛠 Technical fixes

- Splash screen no longer blocks startup if ESPHome is missing; fallback CLI check added.
- Doxygen configuration updated to support Markdown, images, and custom layout.
- Various UI consistency fixes across tabs and dialogs.

---

## 🔔 Version 1.4.0 – Mid Release

### 🧩 Major Features

**• Visual Project Manager**  
- Introduced a new user project manager with visual cards and category grouping.  
- Each project shows name, version, author, description, and changelog.
- Supports quick edit, direct opening, and multilingual adaptation at runtime.

**• Author field**  
- A new “Author” field can be specified during project creation.  
- The data is stored in `info.json` and displayed in the user interface.

**• Advanced project edit dialog**  
- Replaces the old input dialogs with a unified interface for version and changelog update.

**• Incremental changelog tracking**  
- Each change to the version is logged with a timestamp and description in `info.json`.

**• File menu redesign**  
- Refined for better clarity and structured access to actions.

**• Log viewer from settings**  
- Logs are now accessible directly from the settings menu.

**• Description + changelog layout improved**  
- Compact and clear rendering with selectable text support.

### 🌍 Translations

Fully translated into: English, Italian, Spanish, German, Portuguese

### 🛠 Technical improvements

- Proper window language refresh after switching UI language.
- Correct folder naming during project creation.
- Refactored `info.json` write logic and project folder structure.

---

## 🔧 Version 1.3.2

- Log file now supports rotation (20MB max)
- Improved internal exception handling
- Windows 11 compatibility tested

## 🛠 Version 1.3.1

- Fixed first-run language selector issue
- Improved YAML import logic from existing files
- Added new translation keys and label support

---

More details and releases: [GitHub Releases Page](https://github.com/JZ/esphomeguieasy/releases)