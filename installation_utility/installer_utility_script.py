import sys, tarfile, subprocess, os, shutil, io
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def gui_log(msg, log_area=None):
    if log_area:
        # Aggiunge un newline solo se non c'è già
        log_area.insert('end', msg if msg.endswith('\n') else msg + '\n')
        log_area.see('end')
        if getattr(gui_log, "_counter", 0) % 3 == 0:
            log_area.update_idletasks()
        gui_log._counter = getattr(gui_log, "_counter", 0) + 1
    else:
        print(msg)

class TkinterStdout(io.StringIO):
    def __init__(self, log_area):
        super().__init__()
        self.log_area = log_area

    def write(self, s):
        if self.log_area and s.strip() != "":
            self.log_area.insert('end', s)
            self.log_area.see('end')
            self.log_area.update_idletasks()
        return super().write(s)        

def run_external_command(cmd, log_area=None, log_file_path=None):
    """
    Esegue un comando esterno e mostra l'output live sia su log_area (GUI) che su file log.
    Limita la lunghezza della log area per mantenerla fluida.
    """
    import subprocess

    # Apri file log se richiesto
    f = open(log_file_path, "a", encoding="utf-8") if log_file_path else None

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        # Scrivi sempre su file log
        if f:
            f.write(line)
        # Logga in GUI solo se non troppe righe (trim log)
        gui_log(line, log_area)
        if log_area:
            trim_log_area(log_area, max_lines=500)
    if f:
        f.close()
    proc.wait()

def trim_log_area(log_area, max_lines=500):
    lines = int(log_area.index('end-1c').split('.')[0])
    if lines > max_lines:
        log_area.delete('1.0', f"{lines - max_lines}.0")

def get_log_file_name(target):
    return f"log_pack_{target.lower()}_{datetime.now():%Y%m%d_%H%M%S}.txt"


class WindowsPackage():

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

class LinuxPackage():

    # Contenuti da includere nella cartella ESPHomeGUIeasy (installata)
    MAIN_CONTENT = [
        "main.py",
        "config",
        "gui",
        "docs",
        "core",
        "assets",
        "language",
        "installation_utility/user_config.db"
    ]
    PYTHON_FOLDER = "installation_utility/linux/python"  # cartella Python embedded (verrà copiata come "python/")
    LICENSE_FOLDER = "installation_utility/License"

class MacOSPackage():
        
    # Contenuti da includere nella cartella ESPHomeGUIeasy (installata)
    MAIN_CONTENT = [
        "main.py",
        "config",
        "gui",
        "docs",
        "core",
        "assets",
        "language",
        "installation_utility/user_config.db"
    ]
    PYTHON_FOLDER = "installation_utility/python-embed"  # cartella Python embedded (verrà copiata come "python/")
    LICENSE_FOLDER = "installation_utility/License"
    SCRIPT_FOLDER = "installation_utility/setup_builder.iss"    



def ensure_directory(path, log_area=None):
    if not os.path.exists(path):
        os.makedirs(path)
        gui_log(f"✅ Creata cartella: {path}", log_area)
        if log_area: log_area.update()
    else:
        gui_log(f"📁 Cartella già esistente: {path}", log_area)
        if log_area: log_area.update()

def copy_item(item, destination, base_dir, log_area=None):
    src_path = os.path.join(base_dir, item)
    dest_path = os.path.join(destination, os.path.basename(item))

    try:
        if os.path.isdir(src_path):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            gui_log(f"📦 Copiata cartella: {item}", log_area)
            if log_area: log_area.update()
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            gui_log(f"📄 Copiato file: {item}", log_area)
            if log_area: log_area.update()
        else:
            gui_log(f"⚠️ Elemento non trovato: {item}", log_area)
            if log_area: log_area.update()
    except Exception as e:
        gui_log(f"❌ Errore durante la copia di {item}: {e}", log_area)
        if log_area: log_area.update()

def choose_output_directory():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Scegli dove salvare la cartella 'ESPHomeGUIeasy'")
    return folder_selected

def build_windows_installer(output_dir, log_area=None):
    old_stdout = sys.stdout
    sys.stdout = TkinterStdout(log_area)
    try:
        gui_log("📂 Seleziona cartella di destinazione...\n", log_area)
        if log_area: log_area.update()
        target_root = output_dir
        if not target_root:
            gui_log("⛔ Nessuna cartella selezionata. Operazione annullata.", log_area)
            if log_area: log_area.update()
            return


        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        install_dir = os.path.join(target_root, "install", "ESPHomeGUIeasy")
        python_target = os.path.join(install_dir, "python")
        install_root = os.path.join(target_root, "install")

        ensure_directory(install_dir)
        ensure_directory(python_target)

        # Copia contenuto principale
        for item in WindowsPackage.MAIN_CONTENT:
            copy_item(item, install_dir, base_path)

        # Copia Python embedded
        copy_folder_contents(os.path.join(base_path, WindowsPackage.PYTHON_FOLDER), python_target)
        copy_item(WindowsPackage.LICENSE_FOLDER, install_root, base_path)
        copy_item(WindowsPackage.LICENSE_FOLDER, install_dir, base_path)
        copy_item(WindowsPackage.SCRIPT_FOLDER, install_root, base_path)
        create_start_bat(install_dir)
        compile_inno_setup_script(install_root)

        gui_log(f"\n🎉 Cartella di installazione preparata in:\n{install_dir}", log_area)
        if log_area: log_area.update()
    finally:
        sys.stdout = old_stdout        

def copy_folder_contents(src_folder, dest_folder, exclude_ext=None, log_area=None):
    if exclude_ext is None:
        exclude_ext = []
    for item in os.listdir(src_folder):
        if any(item.lower().endswith(ext) for ext in exclude_ext):
            continue
        item_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        if os.path.isdir(item_path):
            shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
            gui_log(f"📦 Copiata sottocartella: {item}", log_area)
            if log_area: log_area.update()
        elif os.path.isfile(item_path):
            shutil.copy2(item_path, dest_path)
            gui_log(f"📄 Copiato file: {item}", log_area)
            if log_area: log_area.update()


def create_start_bat(install_dir, log_area=None):
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
    gui_log("🚀 Creato file esphomeguieasy.bat", log_area)

def create_start_command_mac(install_dir, log_area=None):
    """
    Crea uno script di avvio esphomeguieasy.command per macOS nella cartella di installazione.
    Lo script:
    - imposta la working directory corretta
    - usa python embedded se presente, altrimenti quello di sistema
    - accetta argomenti extra
    """
    cmd_path = os.path.join(install_dir, "esphomeguieasy.command")
    with open(cmd_path, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("cd \"$(dirname \"$0\")\"\n")
        f.write('PYTHON_EXEC="./python/bin/python3"\n')
        f.write('if [ ! -x "$PYTHON_EXEC" ]; then\n')
        f.write('    PYTHON_EXEC="python3"\n')
        f.write('fi\n')
        f.write('echo "Launching ESPHomeGUIeasy using $PYTHON_EXEC..."\n')
        f.write('$PYTHON_EXEC main.py "$@"\n')
    os.chmod(cmd_path, 0o755)
    gui_log("🚀 Creato file esphomeguieasy.command (macOS launch script)", log_area)
    if log_area: log_area.update()


def compile_inno_setup_script(install_root, log_area=None):
    iss_path = os.path.join(install_root, "setup_builder.iss")
    if not os.path.exists(iss_path):
        gui_log("❌ Script .iss non trovato.", log_area)
        return

    gui_log("🛠️ Compilazione setup con Inno Setup...", log_area)
    if log_area: log_area.update()
    try:
        # PATCH: mostra output live
        run_external_command(["ISCC", iss_path], log_area, log_file_path=get_log_file_name("Windows"))
        gui_log("✅ Setup compilato con successo.", log_area)
        if log_area: log_area.update()
    except FileNotFoundError:
        gui_log("❌ Errore: il compilatore ISCC non è nel PATH. Aggiungilo o usa il percorso completo.", log_area)
        if log_area: log_area.update()
    except subprocess.CalledProcessError as e:
        gui_log(f"❌ Errore durante la compilazione: {e}", log_area)
        if log_area: log_area.update()


def build_linux_package(output_dir, log_area=None):
    old_stdout = sys.stdout
    sys.stdout = TkinterStdout(log_area)
    try:    
        gui_log("📦 Creazione pacchetto Linux...", log_area)
        if log_area: log_area.update()

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_root = output_dir
        if not target_root:
            gui_log("⛔ Nessuna cartella selezionata. Operazione annullata.", log_area)
            if log_area: log_area.update()
            return

        install_dir = os.path.join(target_root, "ESPHomeGUIeasy-linux")
        python_target = os.path.join(install_dir, "python")
        ensure_directory(install_dir)
        ensure_directory(python_target)

        # Copia contenuti principali
        for item in LinuxPackage.MAIN_CONTENT:
            copy_item(item, install_dir, base_path)

        # Python embedded
        copy_folder_contents(os.path.join(base_path, LinuxPackage.PYTHON_FOLDER), python_target)
        # Rendi eseguibile il python embedded
        python_exe = os.path.join(python_target, "bin", "python3")
        if os.path.exists(python_exe):
            os.chmod(python_exe, 0o755)


        # Licenza
        copy_item(LinuxPackage.LICENSE_FOLDER, install_dir, base_path)

        # Script di lancio
        shutil.copy2(os.path.join(base_path, "installation_utility/linux", "esphomeguieasy.sh"), install_dir)
        os.chmod(os.path.join(install_dir, "esphomeguieasy.sh"), 0o755)


        # Script di installazione
        install_sh_source = os.path.join(base_path, "installation_utility/linux", "install.sh")
        install_sh_target = os.path.join(install_dir, "install.sh")
        shutil.copy2(install_sh_source, install_sh_target)
        os.chmod(install_sh_target, 0o755)
        gui_log("🚀 Creato file install.sh (Linux install script)", log_area)
        # Forza conversione in formato LF
        with open(install_sh_target, "rb") as f:
            content = f.read().replace(b'\r\n', b'\n')
        with open(install_sh_target, "wb") as f:
            f.write(content)
        gui_log("Converto il file da formato dos a formato unix LF", log_area)

        # ⬅️ Copia how_to_install.md dentro /docs
        howto_src = os.path.join(base_path, "installation_utility/linux", "how_to_install.md")
        howto_dst_dir = os.path.join(install_dir, "docs")
        ensure_directory(howto_dst_dir)
        shutil.copy2(howto_src, os.path.join(howto_dst_dir, "how_to_install.md"))
        gui_log("📝 Aggiunto file how_to_install.md (Linux)", log_area)

        # Rendi eseguibili tutti gli .sh
        for fname in os.listdir(install_dir):
            if fname.endswith('.sh'):
                os.chmod(os.path.join(install_dir, fname), 0o755)

        # Comprimi in tar.gz con nome interno UNIFICATO
        output_tar = os.path.join(target_root, "ESPHomeGUIeasy-linux.tar.gz")
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(install_dir, arcname="ESPHomeGUIeasy")

        gui_log(f"🎉 Pacchetto Linux pronto: {output_tar}", log_area)
        if log_area: log_area.update()
    finally:
        sys.stdout = old_stdout


def build_macos_package(output_dir, log_area=None):
    old_stdout = sys.stdout
    sys.stdout = TkinterStdout(log_area)
    try:    
        gui_log("📦 Creazione pacchetto macOS...", log_area)
        if log_area: log_area.update()

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_root = output_dir
        if not target_root:
            gui_log("⛔ Nessuna cartella selezionata. Operazione annullata.", log_area)
            if log_area: log_area.update()
            return

        # Directory temporanea con nome fisso, sarà la root nel tar.gz
        install_dir = os.path.join(target_root, "ESPHomeGUIeasy-macos")
        python_target = os.path.join(install_dir, "python")
        ensure_directory(install_dir)
        ensure_directory(python_target)

        # Copia contenuti principali
        for item in MacOSPackage.MAIN_CONTENT:
            copy_item(item, install_dir, base_path)

        # Copia Python embedded (come su Linux)
        copy_folder_contents(os.path.join(base_path, MacOSPackage.PYTHON_FOLDER), python_target)

        # Copia licenza
        copy_item(MacOSPackage.LICENSE_FOLDER, install_dir, base_path)

        # Copia install.command e how_to_install.md
        install_cmd_src = os.path.join(base_path, "installation_utility/macOS", "install.command")
        install_cmd_dst = os.path.join(install_dir, "install.command")
        shutil.copy2(install_cmd_src, install_cmd_dst)
        os.chmod(install_cmd_dst, 0o755)
        gui_log("🟢 Aggiunto file install.command", log_area)
        # Forza conversione in formato LF
        with open(install_cmd_dst, "rb") as f:
            content = f.read().replace(b'\r\n', b'\n')
        with open(install_cmd_dst, "wb") as f:
            f.write(content)
        gui_log("Converto il file da formato dos a formato unix LF", log_area)        

        howto_src = os.path.join(base_path, "installation_utility/macOS", "how_to_install.md")
        howto_dst = os.path.join(install_dir, "docs/how_to_install.md")
        shutil.copy2(howto_src, howto_dst)
        gui_log("📝 Aggiunto file how_to_install.md", log_area)

        if log_area:
            log_area.update()

        # Crea lo script di lancio .command
        create_start_command_mac(install_dir)

        # Imposta permessi su .command
        cmd_path = os.path.join(install_dir, "esphomeguieasy.command")
        os.chmod(cmd_path, 0o755)

        # Comprimi tutto in un unico tar.gz
        output_tar = os.path.join(target_root, "ESPHomeGUIeasy-macos.tar.gz")
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(install_dir, arcname="ESPHomeGUIeasy")

        gui_log(f"🎉 Pacchetto macOS pronto: {output_tar}", log_area)
        if log_area: log_area.update()            
    finally:
        sys.stdout = old_stdout