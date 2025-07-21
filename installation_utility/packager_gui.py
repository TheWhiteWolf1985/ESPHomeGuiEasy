import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

# ====== IMPORTA LE TUE FUNZIONI QUI! ======
from installer_utility_script import (
    build_windows_installer,
    build_linux_package,
    build_macos_package
)

# ---- COLORI DARK MODE ----
DARK_BG = "#23272e"
DARK_FG = "#d0d0d0"
ACCENT = "#54c1ff"
BTN_BG = "#393e46"
BTN_FG = "#f0f0f0"
ENTRY_BG = "#23272e"
ENTRY_FG = "#d0d0d0"
COMBO_BG = "#393e46"
COMBO_FG = "#186375"
LOG_BG = "#1c1f24"
LOG_FG = "#b1b1b1"

def start_packaging(target, output_dir, log_area):
    def task():
        log_area.insert(tk.END, f"===> Inizio packaging per {target}...\n")
        log_area.see(tk.END)
        try:
            if target == "Windows":
                build_windows_installer(output_dir, log_area)
            elif target == "Linux":
                build_linux_package(output_dir, log_area)
            elif target == "macOS":
                build_macos_package(output_dir, log_area)
            log_area.insert(tk.END, "===> Operazione completata!\n")
        except Exception as e:
            log_area.insert(tk.END, f"!!! ERRORE: {e}\n")
        log_area.see(tk.END)
    threading.Thread(target=task, daemon=True).start()

def launch_gui_packager():
    root = tk.Tk()
    root.title("ESPHomeGUIeasy Packager")
    root.configure(bg=DARK_BG)

    # ---- TTK STYLE DARK ----
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=DARK_BG, foreground=DARK_FG)
    style.configure("TFrame", background=DARK_BG)
    style.configure("TLabel", background=DARK_BG, foreground=DARK_FG)
    style.configure("TButton", background=BTN_BG, foreground=BTN_FG)
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG, background=ENTRY_BG)
    style.configure("TCombobox", fieldbackground=COMBO_BG, background=COMBO_BG, foreground=COMBO_FG)
    style.map("TButton", background=[("active", ACCENT)])

    # ---- LAYOUT ----
    frm = ttk.Frame(root, padding=20)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Sistema operativo target:").grid(row=0, column=0, sticky="w")
    targets = ["Windows", "Linux", "macOS"]
    selected_target = tk.StringVar(value=targets[0])
    combo = ttk.Combobox(frm, textvariable=selected_target, values=targets, state="readonly")
    combo.grid(row=0, column=1, sticky="ew")

    ttk.Label(frm, text="Cartella destinazione:").grid(row=1, column=0, sticky="w")
    selected_output = tk.StringVar(value="")
    dest_entry = ttk.Entry(frm, textvariable=selected_output, width=40)
    dest_entry.grid(row=1, column=1, sticky="ew")

    def select_output_folder():
        folder = filedialog.askdirectory(title="Scegli cartella di destinazione")
        if folder:
            selected_output.set(folder)
    browse_btn = ttk.Button(frm, text="Sfoglia...", command=select_output_folder)
    browse_btn.grid(row=1, column=2)

    # ---- AREA LOG ----
    log_area = scrolledtext.ScrolledText(frm, width=80, height=20, font=("Consolas", 12),
                                         bg=LOG_BG, fg=LOG_FG, insertbackground="#ffffff", borderwidth=1, relief="flat")
    log_area.grid(row=2, column=0, columnspan=3, pady=15, sticky="ew")

    # ---- BOTTONI ----
    def on_build():
        if not selected_output.get():
            messagebox.showwarning("Attenzione", "Seleziona una cartella di destinazione!")
            return
        log_area.delete(1.0, tk.END)
        start_packaging(selected_target.get(), selected_output.get(), log_area)

    def open_folder():
        path = selected_output.get()
        if path and os.path.isdir(path):
            if os.name == "nt":
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')      

    def clear_log():
        log_area.delete(1.0, tk.END)                  

    build_btn = ttk.Button(frm, text="Crea pacchetto", command=on_build)
    build_btn.grid(row=3, column=0, padx=2, pady=10, sticky="ew")

    btn_open_folder = ttk.Button(frm, text="Apri cartella", command=open_folder)
    btn_open_folder.grid(row=3, column=1, padx=2, pady=10, sticky="ew")

    btn_clear_log = ttk.Button(frm, text="Azzera log", command=clear_log)
    btn_clear_log.grid(row=3, column=2, padx=2, pady=10, sticky="ew")

    # All'inizio/fine layout, per larghezza uniforme:
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=1)
    frm.columnconfigure(2, weight=1)

    root.mainloop()

# ---- LANCIO GUI ----
if __name__ == "__main__":
    launch_gui_packager()
