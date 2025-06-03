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
        self.log_callback = log_callback  # Funzione per loggare (es: self.logger.log)
        self.project_dir = None  # Da impostare quando apri/carichi progetto
        self.temp_path = None
        self.process = None
        self.on_compile_finished = None  # Callback per riattivare bottoni

    def set_project_dir(self, path):
        self.project_dir = path        

    def compile_yaml(self, yaml_text: str):
        """
        Salva il testo YAML su file temporaneo o in progetto e avvia la compilazione ESPHome in modo asincrono.
        """
        try:
            # --- Salvataggio file YAML ---
            if self.project_dir and os.path.isdir(self.project_dir):
                # Salva nella cartella progetto
                proj_name = os.path.basename(self.project_dir)
                yaml_path = os.path.join(self.project_dir, f"{proj_name}.yaml")
                with open(yaml_path, "w", encoding="utf-8") as temp_file:
                    temp_file.write(yaml_text)
                self.temp_path = yaml_path
                if self.log_callback:
                    self.log_callback(f"📦 File di progetto creato: {self.temp_path}")
            else:
                # Salva come file temporaneo
                with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w", encoding="utf-8") as temp_file:
                    temp_file.write(yaml_text)
                    self.temp_path = temp_file.name
                if self.log_callback:
                    self.log_callback(f"📦 File temporaneo creato: {self.temp_path}")

            if self.log_callback:
                self.log_callback("🚀 Avvio compilazione...")

            # --- Avvia QProcess ---
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.finished.connect(self.handle_finished)
            self.process.start("esphome", ["compile", self.temp_path])
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"💥 Errore durante la compilazione: {e}")
            if self.temp_path and os.path.exists(self.temp_path):
                os.remove(self.temp_path)
                if self.log_callback:
                    self.log_callback(f"🧹 File temporaneo eliminato: {self.temp_path}")

    def handle_stdout(self):
        if not self.process:
            return
        output = self.process.readAllStandardOutput().data().decode()
        # Colora in base al contenuto della linea
        for line in output.splitlines():
            if "error" in line.lower():
                self.log_callback(line.strip(), "error")
            elif "warning" in line.lower():
                self.log_callback(line.strip(), "warning")
            else:
                self.log_callback(line.strip(), "info")

    def handle_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.log_callback("✅ Compilazione completata con successo.", "success")
        else:
            self.log_callback(f"❌ Errore durante la compilazione. Codice: {exitCode}", "error")
        # Pulizia SOLO se file temporaneo (non file progetto!)
        if self.temp_path:
            temp_dir = tempfile.gettempdir()
            if self.temp_path.startswith(temp_dir):
                if os.path.exists(self.temp_path):
                    os.remove(self.temp_path)
                    self.log_callback(f"🧹 File temporaneo eliminato: {self.temp_path}", "info")
        self.temp_path = None
        self.process = None
        # (NEW) Callback per la GUI
        if hasattr(self, "on_compile_finished") and self.on_compile_finished:
            self.on_compile_finished()
        # (NEW, facoltativo) segnale Qt
            self.compile_finished.emit(exitCode)


    def upload_via_usb(self, yaml_path, com_port):
        """
        Carica il firmware su ESP via porta seriale usando ESPHome CLI.
        """
        from PyQt6.QtCore import QProcess
        if self.log_callback:
            self.log_callback(f"🚀 Avvio upload via USB su {com_port}...")

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.handle_finished_upload)
        self.process.start("esphome", ["upload", yaml_path, "--device", com_port])

    def handle_finished_upload(self, exitCode, exitStatus):
        if exitCode == 0:
            self.log_callback("✅ Upload completato con successo!", "success")
        else:
            self.log_callback(f"❌ Errore durante l'upload. Codice: {exitCode}", "error")
        if hasattr(self, "on_upload_finished") and self.on_upload_finished:
            self.on_upload_finished()
        self.process = None
