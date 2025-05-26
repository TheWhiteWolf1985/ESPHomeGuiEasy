"""
@file compile_manager.py
@brief Contiene la classe CompileManager per la gestione della compilazione ESPHome.

Questa classe prende in input il contenuto YAML, lo salva su file temporaneo,
e lancia il comando `esphome compile` intercettando l'output.
"""

import subprocess
import tempfile
import os


class CompileManager:
    """
    @class CompileManager
    @brief Gestisce la compilazione di file YAML tramite ESPHome.
    """

    def __init__(self, log_callback):
        """
        @brief Costruttore del CompileManager.
        @param log_callback Funzione di callback per stampare log in console GUI.
        """
        self.log_callback = log_callback

    def compile_yaml(self, yaml_text: str):
        """
        @brief Salva il testo YAML su file temporaneo ed esegue la compilazione ESPHome.
        @param yaml_text Il contenuto YAML da compilare.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w", encoding="utf-8") as temp_file:
                temp_file.write(yaml_text)
                temp_path = temp_file.name

            self.log_callback(f"📦 File temporaneo creato: {temp_path}")
            self.log_callback("🚀 Avvio compilazione...")

            process = subprocess.Popen(
                ["esphome", "compile", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            for line in process.stdout:
                self.log_callback(line.strip())

            process.wait()

            if process.returncode == 0:
                self.log_callback("✅ Compilazione completata con successo.")
            else:
                self.log_callback(f"❌ Errore durante la compilazione. Codice: {process.returncode}")

        except Exception as e:
            self.log_callback(f"💥 Errore durante la compilazione: {e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                self.log_callback(f"🧹 File temporaneo eliminato: {temp_path}")
