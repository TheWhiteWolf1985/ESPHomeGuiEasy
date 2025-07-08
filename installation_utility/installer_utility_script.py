import os
import shutil
import tkinter as tk
from tkinter import filedialog
import subprocess
import sys


# Contenuti da includere nella cartella ESPHomeGUIeasy (installata)
MAIN_CONTENT = [
    "main.py",
    "config",
    "gui",
    "docs",
    "core",
    "assets",
    "language",
    "installation_utility/esphomeguieasy.exe",
    "installation_utility/user_config.db"
]


PYTHON_FOLDER = "installation_utility/python-embed"  # cartella Python embedded (verrà copiata come "python/")
LICENSE_FOLDER = "installation_utility/License"
SCRIPT_FOLDER = "installation_utility/setup_builder.iss"

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Creata cartella: {path}")
    else:
        print(f"📁 Cartella già esistente: {path}")

def copy_item(item, destination, base_dir):
    src_path = os.path.join(base_dir, item)
    dest_path = os.path.join(destination, os.path.basename(item))

    try:
        if os.path.isdir(src_path):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"📦 Copiata cartella: {item}")
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"📄 Copiato file: {item}")
        else:
            print(f"⚠️ Elemento non trovato: {item}")
    except Exception as e:
        print(f"❌ Errore durante la copia di {item}: {e}")

def choose_output_directory():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Scegli dove salvare la cartella 'ESPHomeGUIeasy'")
    return folder_selected

def build_installer_folder():
    print("📂 Seleziona cartella di destinazione...\n")
    target_root = choose_output_directory()
    if not target_root:
        print("⛔ Nessuna cartella selezionata. Operazione annullata.")
        return

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    install_dir = os.path.join(target_root, "install", "ESPHomeGUIeasy")
    python_target = os.path.join(install_dir, "python")
    install_root = os.path.join(target_root, "install")

    ensure_directory(install_dir)
    ensure_directory(python_target)

    # Copia contenuto principale
    for item in MAIN_CONTENT:
        copy_item(item, install_dir, base_path)

    # Copia Python embedded
    copy_folder_contents(os.path.join(base_path, PYTHON_FOLDER), python_target)
    copy_item(LICENSE_FOLDER, install_root, base_path)
    copy_item(LICENSE_FOLDER, install_dir, base_path)
    copy_item(SCRIPT_FOLDER, install_root, base_path)
    create_start_bat(install_dir)
    compile_inno_setup_script(install_root)


    print(f"\n🎉 Cartella di installazione preparata in:\n{install_dir}")

def copy_folder_contents(src_folder, dest_folder):
    for item in os.listdir(src_folder):
        item_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)

        if os.path.isdir(item_path):
            shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
            print(f"📦 Copiata sottocartella: {item}")
        elif os.path.isfile(item_path):
            shutil.copy2(item_path, dest_path)
            print(f"📄 Copiato file: {item}")

def create_start_bat(install_dir):
    bat_path = os.path.join(install_dir, "esphomeguieasy.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %%~dp0\n")
        f.write("echo Avvio ESPHomeGUIeasy... > \"%%TEMP%%\\esphomeguieasy_log.txt\"\n")
        f.write("python\\ESPHomeRunner.exe main.py >> \"%%TEMP%%\\esphomeguieasy_log.txt\" 2>&1\n")
        f.write("if errorlevel 1 (\n")
        f.write("    echo Errore durante l'esecuzione. Controlla il file di log in %%TEMP%%\\esphomeguieasy_log.txt\n")
        f.write("    pause\n")
        f.write(")\n")
    print("🚀 Creato file esphomeguieasy.bat")


def compile_inno_setup_script(install_root):
    iss_path = os.path.join(install_root, "setup_builder.iss")
    if not os.path.exists(iss_path):
        print("❌ Script .iss non trovato.")
        return

    print("🛠️ Compilazione setup con Inno Setup...")
    try:
        # Usa il comando ISCC (Inno Setup Compiler), presupponendo che sia nel PATH
        subprocess.check_call(["ISCC", iss_path])
        print("✅ Setup compilato con successo.")
    except FileNotFoundError:
        print("❌ Errore: il compilatore ISCC non è nel PATH. Aggiungilo o usa il percorso completo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante la compilazione: {e}")



if __name__ == "__main__":
    build_installer_folder()
