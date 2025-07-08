# -*- coding: utf-8 -*-
"""
@file compile_manager.py
@brief Manages the compilation, upload, and flashing of ESPHome YAML files via QProcess and subprocess.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Implements the CompileManager class to:
- Run `esphome compile` for selected YAML files
- Upload via USB using `esphome run`
- Detect connected ESP chips via `esptool`
- Perform flash erase and output structured logs to the GUI

Also emits Qt signals to synchronize with the GUI during operations.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtCore import QObject, QProcess, pyqtSignal, Qt, QMetaObject, Q_ARG
from PyQt6.QtWidgets import QMessageBox, QApplication
import tempfile, os, socket, threading, sys, subprocess, re
from ruamel.yaml import YAML

class CompileManager(QObject):
    """
    @brief Controls ESPHome-related build and upload operations for a given project.

    Uses QProcess for asynchronous execution and emits signals to update the UI.
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
        @brief Starts ESPHome compilation for the specified YAML file.

        @param yaml_path Absolute path to the YAML file to be compiled.
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
        """
        @brief Processes live output from the ESPHome compile command.
        """        
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
        """
        @brief Processes live output from the ESPHome compile command.
        """        
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
        """
        @brief Uploads the firmware to the board via USB using ESPHome CLI.

        @param yaml_path Path to the YAML configuration file.
        @param com_port The COM port (e.g., COM3, /dev/ttyUSB0) to which the board is connected.
        """
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
        """
        @brief Uses esptool to erase the ESP chip's flash memory.

        @param com_port The COM port to use for the erase operation.
        """
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
        """
        @brief Processes live output from the ESPHome compile command.
        """        
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
        """
        @brief Processes live output from the ESPHome compile command.
        """        
        if exitCode == 0:
            self.log_callback("✅ Memoria cancellata con successo", "success")
        else:
            self.log_callback(f"❌ Errore durante la cancellazione. Codice: {exitCode}", "error")

        self.upload_finished.emit()  # Riutilizziamo il segnale per sbloccare la GUI
        self.process = None


           
    def detect_connected_chip(self, com_port):
        """
        @brief Uses esptool to detect the chip model connected via USB.

        @param com_port The serial port used for communication.
        @return Detected chip type as string (e.g., "ESP32-C3") or None if not found.
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
        """
        @brief Processes live output from the ESPHome compile command.
        """
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
        """
        @brief Processes live output from the ESPHome compile command.
        """        
        if exitCode != 0:
            self.log_callback(f"❌ Upload terminato con errore (codice: {exitCode}).", "error")

        self.upload_finished.emit()  # segnale Qt ufficiale
        self.process = None


