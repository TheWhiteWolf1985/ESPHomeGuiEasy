import os
import shutil
import tkinter as tk
from tkinter import filedialog
import subprocess
import sys


# Contenuti da includere nella cartella ESPHomeGUIeasy (installata)
MAIN_CONTENT = [
    "main.py",
    "docs",
    "config",
    "community_project",
    "gui",
    "build",
    "core",
    "assets",
    "language",
    "requirements.txt",
    "installation_utility/esphomeguieasy.exe"
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
    create_venv_and_install_requirements(install_dir, base_path)
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

def create_venv_and_install_requirements(install_dir, base_path):
    venv_path = os.path.join(install_dir, "venv")
    print("🐍 Creo ambiente virtuale...")

    python_embed_exe = os.path.join(base_path, PYTHON_FOLDER, "python.exe")
    subprocess.check_call([python_embed_exe, "-m", "venv", venv_path])

    pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    requirements_file = os.path.join(base_path, "requirements.txt")

    print("⬆️ Aggiorno pip all'ultima versione...")
    subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])

    print("📦 Installo dipendenze da requirements.txt...")
    subprocess.check_call([pip_exe, "install", "-r", requirements_file])

    clean_venv(venv_path)


def clean_venv(venv_path):
    print("🧹 Pulizia del venv...")

    import fnmatch

    def remove_by_pattern(base, pattern):
        for root, dirs, files in os.walk(base):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    try:
                        os.remove(os.path.join(root, filename))
                        print(f"🗑️ Rimosso: {filename}")
                    except:
                        pass

    def remove_dirs_named(base, names):
        for root, dirs, _ in os.walk(base):
            for d in dirs:
                if d.lower() in names:
                    dirpath = os.path.join(root, d)
                    try:
                        shutil.rmtree(dirpath)
                        print(f"🗑️ Rimossa cartella: {dirpath}")
                    except:
                        pass

    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    remove_dirs_named(site_packages, ["tests", "test", "testing", "__pycache__"])
    remove_by_pattern(site_packages, "*.pyc")
    remove_by_pattern(site_packages, "*.pyo")
    remove_by_pattern(site_packages, "*.egg-info")

    bin_path = os.path.join(venv_path, "Scripts")
    for name in ["pip.exe", "pip3.exe", "easy_install.exe"]:
        path = os.path.join(bin_path, name)
        if os.path.exists(path):
            os.remove(path)
            print(f"🗑️ Rimosso: {name}")

def create_start_bat(install_dir):
    bat_path = os.path.join(install_dir, "start_gui.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %%~dp0\n")
        f.write("call venv\\Scripts\\activate.bat\n")
        f.write("python main.py\n")
    print("🚀 Creato file start_gui.bat")

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
