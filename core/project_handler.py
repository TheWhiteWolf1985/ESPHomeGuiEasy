import threading
import os
import zipfile
from core.translator import Translator
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from gui.progress_dialog import ProgressDialog

class ImportWorker(QObject):
    progress = pyqtSignal(int, int)   # (current, total)
    finished = pyqtSignal(str, str)   # path_yaml, path_zip

    def __init__(self, path_zip, path_dest):
        super().__init__()
        self.path_zip = path_zip
        self.path_dest = path_dest

    def run(self):
        import os, zipfile
        base_name = os.path.splitext(os.path.basename(self.path_zip))[0]
        final_proj_dir = os.path.join(self.path_dest, base_name)
        os.makedirs(final_proj_dir, exist_ok=True)

        yaml_found = None
        try:
            with zipfile.ZipFile(self.path_zip, 'r') as zipf:
                filelist = zipf.namelist()
                total = len(filelist)
                for i, member in enumerate(filelist, 1):
                    zipf.extract(member, final_proj_dir)
                    self.progress.emit(i, total)
            for root, dirs, files in os.walk(final_proj_dir):
                for file in files:
                    if file.endswith(".yaml") or file.endswith(".yml"):
                        yaml_found = os.path.join(root, file)
                        break
                if yaml_found:
                    break
        except Exception as e:
            yaml_found = None
        self.finished.emit(yaml_found or "", self.path_zip)

##########################################################################
#                                                                        #
##########################################################################        

class ExportWorker(QObject):
    progress = pyqtSignal(int, int)    # (current, total)
    finished = pyqtSignal(str)         # path_zip

    def __init__(self, project_dir, path_zip):
        super().__init__()
        self.project_dir = project_dir
        self.path_zip = path_zip

    def run(self):
        filelist = []
        for root, dirs, files in os.walk(self.project_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, self.project_dir)
                if not rel_path.startswith('.pioenvs'):
                    filelist.append((abs_path, rel_path))
        total = len(filelist)
        try:
            with zipfile.ZipFile(self.path_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, (abs_path, rel_path) in enumerate(filelist, 1):
                    zipf.write(abs_path, rel_path)
                    self.progress.emit(i, total)
            self.finished.emit(self.path_zip)
        except Exception:
            self.finished.emit("")        

##########################################################################
#                                                                        #
##########################################################################           

class ProjectHandler:
    @staticmethod
    def export_project(project_dir, save_dialog, logger, parent_gui=None):
        # Chiedi path zip PRIMA di partire col thread!
        nome_progetto = os.path.basename(project_dir)
        path_zip, _ = save_dialog(
            None, "Esporta progetto", f"{nome_progetto}.zip", "Archivio ZIP (*.zip)"
        )
        if not path_zip:
            return

        worker = ExportWorker(project_dir, path_zip)
        thread = QThread()
        worker.moveToThread(thread)

        # --- Crea progress dialog ---
        progress_dialog = ProgressDialog(
            "Esportazione progetto in corso...",
            "Compressione file...",
            parent=parent_gui
        )
        progress_dialog.show()

        def on_progress(current, total):
            progress_dialog.set_progress(current, total)

        def on_finished(zip_path):
            progress_dialog.close()
            if zip_path and os.path.exists(zip_path):
                logger(f"📦 Progetto esportato come {zip_path}", "success")
            else:
                logger("Errore esportazione progetto!", "error")
            thread.quit()
            thread.wait()
            worker.deleteLater()
            thread.deleteLater()

        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        thread.started.connect(worker.run)
        thread.start()

    @staticmethod
    def import_project(open_dialog, dir_dialog, logger, open_project_callback):
        path_zip, _ = open_dialog(None, "Importa progetto", "", "Archivio ZIP (*.zip)")
        if not path_zip:
            return
        path_dest = dir_dialog(None, "Seleziona cartella di destinazione")
        if not path_dest:
            return

        worker = ImportWorker(path_zip, path_dest)
        thread = QThread()
        worker.moveToThread(thread)

        # --- Crea la progress dialog ---
        progress_dialog = ProgressDialog("Importazione progetto in corso...")
        progress_dialog.show()

        def on_progress(current, total):
            progress_dialog.set_progress(current, total)

        def on_finished(yaml_path, zip_path):
            progress_dialog.close()
            if yaml_path and os.path.exists(yaml_path):
                open_project_callback(yaml_path)
                logger(f"📂 Progetto importato da {zip_path}", "success")
            else:
                logger("Nessun file YAML trovato nell’archivio importato.", "error")
            thread.quit()
            thread.wait()
            worker.deleteLater()
            thread.deleteLater()

        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        thread.started.connect(worker.run)
        thread.start()