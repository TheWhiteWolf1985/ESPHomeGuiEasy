from PyQt6.QtCore import QObject, QProcess, pyqtSignal, Qt, QMetaObject, Q_ARG
from PyQt6.QtWidgets import QMessageBox, QApplication
import tempfile, os, socket, threading, sys, subprocess, re
from ruamel.yaml import YAML


class CompileManager(QObject):
    """
    Gestisce la compilazione di file YAML tramite ESPHome usando QProcess.
    """
    compile_finished = pyqtSignal(int)  # Segnale con codice di uscita
    upload_finished = pyqtSignal()

    def __init__(self, log_callback, parent=None):
        super().__init__(parent)
        self.log_callback = log_callback or print  # Funzione per loggare (es: self.logger.log)   
        self.project_dir = None  # Da impostare quando apri/carichi progetto
        self.temp_path = None
        self.process = None
        self.window = None

    def set_project_dir(self, path):
        self.project_dir = path        

    def compile_yaml(self, yaml_path: str):
        """
        Avvia la compilazione ESPHome sul file YAML specificato.
        """
        try:
            self.temp_path = yaml_path
            self.log_callback("🚀 Avvio compilazione...")

            if self.process:
                self.process.kill()
                self.process.deleteLater()

            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_compile_output)
            self.process.finished.connect(self.handle_compile_finished)
            self.process.start("esphome", ["compile", yaml_path])

        except Exception as e:
            self.log_callback(f"💥 Errore durante la compilazione: {e}")
            
    def handle_compile_output(self):
        if not self.process:
            return
        output = self.process.readAllStandardOutput().data().decode()
        for line in output.splitlines():
            if "error" in line.lower():
                self.log_callback(line.strip(), "error")
            elif "warning" in line.lower():
                self.log_callback(line.strip(), "warning")
            else:
                self.log_callback(line.strip(), "info") 

    def handle_compile_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.log_callback("✅ Compilazione completata con successo.", "success")
        else:
            self.log_callback(f"❌ Errore durante la compilazione. Codice: {exitCode}", "error")

        # Pulizia file temporaneo
        if self.temp_path:
            temp_dir = tempfile.gettempdir()
            if self.temp_path.startswith(temp_dir):
                if os.path.exists(self.temp_path):
                    os.remove(self.temp_path)
                    self.log_callback(f"🧹 File temporaneo eliminato: {self.temp_path}", "info")
        self.temp_path = None
        self.process = None

        # Segnale per la GUI
        self.compile_finished.emit(exitCode)



    def upload_via_usb(self, yaml_path, com_port):
        self.log_callback(f"📤 Upload in corso su {com_port}...")

        self.yaml_path = yaml_path
        self.com_port = com_port

        # Costruisci il comando
        self.command = ["esphome", "run", yaml_path, "--device", com_port, "--no-logs"]

        # Istanzia QProcess se non esiste
        if self.process:
            self.process.kill()
            self.process.deleteLater()
            self.process = None

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_upload_output)
        self.process.finished.connect(self.handle_upload_finished)

        self.process.start(self.command[0], self.command[1:])

    def erase_flash(self, com_port):
        command = [sys.executable, "-m", "esptool", "--port", com_port, "erase_flash"]

        if self.process:
            self.process.kill()
            self.process.deleteLater()
            self.process = None

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_erase_output)
        self.process.finished.connect(self.handle_erase_finished)

        self.process.start(command[0], command[1:])

    def handle_erase_output(self):
        if not self.process:
            return

        output = self.process.readAllStandardOutput().data().decode()
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            if "erasing flash" in line.lower():
                self.log_callback("📀 Cancellazione in corso...", "info")
            elif "chip is" in line.lower():
                self.log_callback(line, "info")
            elif "error" in line.lower():
                self.log_callback(line, "error")
            else:
                self.log_callback(line, "info")

    def handle_erase_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.log_callback("✅ Memoria cancellata con successo", "success")
        else:
            self.log_callback(f"❌ Errore durante la cancellazione. Codice: {exitCode}", "error")

        self.upload_finished.emit()  # Riutilizziamo il segnale per sbloccare la GUI
        self.process = None


           
    def detect_connected_chip(self, com_port):
        """
        Usa esptool per rilevare il chip connesso su COM.
        Ritorna una stringa tipo 'ESP32-C3', oppure None in caso di errore.
        """
        try:
            self.log_callback(f"🔍 Rilevo chip su {com_port}...")

            command = [sys.executable, "-m", "esptool", "--port", com_port, "chip_id"]
            result = subprocess.run(command, capture_output=True, text=True)
            print("📍 DEBUG: sono in upload_via_usb()")


            stdout = result.stdout
            stderr = result.stderr

            if stdout:
                self.log_callback(stdout, "info")
                match = re.search(r"Chip is (.+?)\\s", stdout)
                if match:
                    chip_type = match.group(1).strip()
                    self.log_callback(f"📟 Chip rilevato: {chip_type}", "info")
                    return chip_type

            if stderr:
                self.log_callback(stderr, "error")

        except Exception as e:
            self.log_callback(f"❌ Errore nel rilevamento chip: {e}", "error")

        return None
    
    def handle_upload_output(self):
        if not self.process:
            return

        output = self.process.readAllStandardOutput().data().decode()
        lines = [l.strip() for l in output.splitlines() if l.strip()]
        for line in lines:
            # Log live ogni riga
            self.log_callback(line, "info")

            # Rileva completamento
            if "error" in line.lower():
                self.log_callback(line, "error")
            # rimuoviamo il log di successo da qui

    def handle_upload_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.log_callback(f"❌ Upload terminato con errore (codice: {exitCode}).", "error")

        self.upload_finished.emit()  # segnale Qt ufficiale
        self.process = None


