from PyQt6.QtCore import QObject, QProcess, pyqtSignal
import tempfile
import os

class CompileManager(QObject):
    """
    Gestisce la compilazione di file YAML tramite ESPHome usando QProcess.
    """
    compile_finished = pyqtSignal(int)  # Segnale con codice di uscita

    def __init__(self, log_callback, parent=None):
        super().__init__(parent)
        self.log_callback = log_callback
        self.process = None
        self.temp_path = None
        self.project_dir = None

    def compile_yaml(self, yaml_text: str):
        """
        Salva il testo YAML su file temporaneo e avvia la compilazione ESPHome in modo asincrono.
        """
        try:
            if self.project_dir and os.path.isdir(self.project_dir):
                # Salva il file YAML direttamente nella cartella di progetto
                proj_name = os.path.basename(self.project_dir)
                yaml_path = os.path.join(self.project_dir, f"{proj_name}.yaml")
                with open(yaml_path, "w", encoding="utf-8") as temp_file:
                    temp_file.write(yaml_text)
                self.temp_path = yaml_path
                self.log_callback(f"📦 File di progetto creato: {self.temp_path}")
            else:
                # Fallback su file temporaneo
                with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w", encoding="utf-8") as temp_file:
                    temp_file.write(yaml_text)
                    self.temp_path = temp_file.name
                self.log_callback(f"📦 File temporaneo creato: {self.temp_path}")

            self.log_callback("🚀 Avvio compilazione...")

            # Avvia QProcess
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.finished.connect(self.handle_finished)
            self.process.start("esphome", ["compile", self.temp_path])
        except Exception as e:
            self.log_callback(f"💥 Errore durante la compilazione: {e}")
            if self.temp_path and os.path.exists(self.temp_path):
                os.remove(self.temp_path)
                self.log_callback(f"🧹 File temporaneo eliminato: {self.temp_path}")

    def handle_stdout(self):
        if self.process is not None:
            out = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
            for line in out.splitlines():
                self.log_callback(line)

    def handle_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.log_callback("✅ Compilazione completata con successo.")
        else:
            self.log_callback(f"❌ Errore durante la compilazione. Codice: {exitCode}")
        # Pulizia SOLO se file temporaneo (non file progetto!)
        if self.temp_path:
            # Cancella solo se è effettivamente in temp (cartella di sistema)
            temp_dir = tempfile.gettempdir()
            if self.temp_path.startswith(temp_dir):
                if os.path.exists(self.temp_path):
                    os.remove(self.temp_path)
                    self.log_callback(f"🧹 File temporaneo eliminato: {self.temp_path}")
        self.temp_path = None
        self.process = None
        self.compile_finished.emit(exitCode)


    def set_project_dir(self, path):
        self.project_dir = path