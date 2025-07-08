# -*- coding: utf-8 -*-
"""
@file tab_command.py
@brief Tab for managing compilation, USB upload, OTA upload, and erase flash commands.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Provides the UI and logic for flashing firmware to ESP devices via USB serial or OTA.
Includes controls for baud rate, COM port selection, network scanning for OTA,
and buttons to start compile, upload, erase, and test connections.

Manages command concurrency and updates UI button states accordingly.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QLabel, QComboBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSlot
import socket, threading, os
import serial.tools.list_ports  # Richiede pyserial
from PyQt6.QtGui import QPalette, QColor
from gui.color_pantone import Pantone
from core.translator import Translator
from core.compile_manager import CompileManager
from pathlib import Path
from core.log_handler import GeneralLogHandler as logger
from config.GUIconfig import DEFAULT_BUILD_DIR


class TabCommand(QWidget):
    """
    @brief Manages the command interface tab for compiling and uploading ESPHome firmware.

    Initializes UI elements for USB serial loader and OTA uploading,
    including baud rate selection, COM port refresh, IP scanning, and firmware upload buttons.

    Handles threading to prevent concurrent commands and updates UI accordingly.

    Emits logging messages for all actions and errors.
    """
    def __init__(self, yaml_editor, logger, compiler, flash_callback=None, ota_callback=None):
        """
        @brief Sets up the command tab UI components and connects signals to slots.

        Configures color palette for dark theme, groups controls into USB and OTA sections,
        and sets up compile group with compile button.

        Connects buttons to corresponding methods and prepares UI layouts.
        """
        super().__init__()
        self.yaml_editor = yaml_editor
        self.logger = logger
        self.compiler = compiler
        self.busy = False  # Blocca comandi concorrenti (compile/erase/upload
        self.compiler.upload_finished.connect(self.riabilita_bottoni_qt)
        self.compiler.compile_finished.connect(self.riabilita_bottoni_qt)


        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#5f1717"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#3a9dda"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2a2d2e"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))

        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)           

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Sezione USB / Serial Loader (layout verticale e allineato) ---
        self.usb_box = QGroupBox(Translator.tr("usb_serial_loader"))
        self.usb_box.setStyleSheet(Pantone.GROUPBOX_STYLE)
        usb_vlayout = QVBoxLayout()

        usb_form = QFormLayout()
        usb_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        usb_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        # Baud rate
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "57600", "115200", "230400", "460800", "921600"])
        self.baud_combo.setCurrentText("115200")
        self.baud_combo.setFixedWidth(120)
        usb_form.addRow(Translator.tr("baud"), self.baud_combo)

        # Porta COM + Refresh
        com_row = QHBoxLayout()
        self.com_combo = QComboBox()
        self.com_combo.setFixedWidth(200)
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(40)
        refresh_btn.setStyleSheet("""
            QPushButton { background-color: #3a9dda; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #2277aa; }
        """)
        refresh_btn.clicked.connect(self.refresh_com_ports)
        com_row.addWidget(self.com_combo)
        com_row.addWidget(refresh_btn)
        usb_form.addRow(Translator.tr("port"), com_row)

        usb_vlayout.addLayout(usb_form)

        # Riga bottoni azione
        usb_btn_row = QHBoxLayout()

        self.erase_btn = QPushButton("🧹 " + Translator.tr("erase_flash"))
        self.erase_btn.setFixedWidth(170)
        self.erase_btn.clicked.connect(self.erase_flash)
        self.erase_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.flash_btn = QPushButton("📤 " + Translator.tr("upload"))
        self.flash_btn.setFixedWidth(170)
        self.flash_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        refresh_btn.clicked.connect(self.refresh_com_ports)
        self.flash_btn.clicked.connect(self.carica_firmware)

        usb_btn_row.addWidget(self.erase_btn)
        usb_btn_row.addWidget(self.flash_btn)
        usb_btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usb_vlayout.addLayout(usb_btn_row)

        self.usb_box.setLayout(usb_vlayout)
        layout.addWidget(self.usb_box)


        # --- Sezione OTA (WiFi, layout verticale e allineato) ---
        self.ota_box = QGroupBox(Translator.tr("ota_wifi"))
        self.ota_box.setStyleSheet(Pantone.GROUPBOX_STYLE)
        ota_vlayout = QVBoxLayout()

        # Riga 1: Scansione + combo IP trovati
        scan_row = QHBoxLayout()
        self.scan_btn = QPushButton(Translator.tr("scan_network"))
        self.scan_btn.setFixedWidth(160)
        self.scan_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.scan_btn.clicked.connect(self.scan_network_for_esp)
        self.ip_combo = QComboBox()
        self.ip_combo.setFixedWidth(230)
        self.ip_combo.setEditable(False)
        self.ip_combo.currentIndexChanged.connect(self.on_combo_ip_selected)
        scan_row.addWidget(self.scan_btn)
        scan_row.addWidget(self.ip_combo)
        ota_vlayout.addLayout(scan_row)

        # Form layout per campi IP, Porta, Password
        ota_form = QFormLayout()
        ota_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ota_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        self.ota_ip_edit = QLineEdit()
        self.ota_ip_edit.setPlaceholderText("es: 192.168.1.100")
        self.ota_ip_edit.setFixedWidth(230)
        ota_form.addRow(Translator.tr("ip_address"), self.ota_ip_edit)

        self.ota_port_edit = QLineEdit()
        self.ota_port_edit.setText("3232")
        self.ota_port_edit.setFixedWidth(80)
        ota_form.addRow(Translator.tr("ota_port"), self.ota_port_edit)

        self.ota_pwd_edit = QLineEdit()
        self.ota_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.ota_pwd_edit.setFixedWidth(230)
        ota_form.addRow(Translator.tr("ota_password"), self.ota_pwd_edit)

        ota_vlayout.addLayout(ota_form)

        # Riga bottoni finali (Test/Carica)
        ota_btn_row = QHBoxLayout()
        self.test_ota_btn = QPushButton(Translator.tr("test_connection"))
        self.test_ota_btn.setFixedWidth(170)
        self.test_ota_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.flash_ota_btn = QPushButton(Translator.tr("flash_ota"))
        self.flash_ota_btn.setFixedWidth(170)
        self.flash_ota_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.scan_btn.clicked.connect(self.scan_network_for_esp)
        self.ip_combo.currentIndexChanged.connect(self.on_combo_ip_selected)
        self.test_ota_btn.clicked.connect(self.test_ota_connection)
        self.flash_ota_btn.clicked.connect(self.flash_via_ota)

        ota_btn_row.addWidget(self.test_ota_btn)
        ota_btn_row.addWidget(self.flash_ota_btn)
        ota_btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ota_vlayout.addLayout(ota_btn_row)

        self.ota_box.setLayout(ota_vlayout)
        layout.addWidget(self.ota_box)

        # --- SEZIONE COMPILAZIONE ---
        self.group_compile = QGroupBox(Translator.tr("firmware_compile"))
        self.group_compile.setStyleSheet(Pantone.GROUPBOX_STYLE)
        group_layout = QVBoxLayout()

        # Bottone COMPILA
        self.compile_btn = QPushButton("🚀 " + Translator.tr("compile"))
        self.compile_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        self.compile_btn.setFixedWidth(200)
        self.compile_btn.clicked.connect(self.compila_progetto)


        # Layout bottoni
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.addWidget(self.compile_btn)

        group_layout.addLayout(btn_layout)
        self.group_compile.setLayout(group_layout)
        layout.addWidget(self.group_compile)
 

    def refresh_com_ports(self):
        """
        @brief Refreshes the list of available COM ports for USB flashing.

        Queries system serial ports and populates the COM port dropdown.
        Shows a warning entry if no ports are found.
        """
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_combo.addItem(f"{port.device} ({port.description})", port.device)
        if not ports:
            self.com_combo.addItem(Translator.tr("no_port_found"), "")

    def carica_firmware(self):
        """
        @brief Starts USB firmware upload process.

        Disables buttons to prevent concurrent commands.
        Determines YAML file path to upload, logs firmware path if found.
        Checks that a COM port is selected, then calls the compiler upload method.
        """
        if self.busy:
            logger.debug("DEBUG: comando upload ignorato perché busy = True")
            return

        self.busy = True
        self.compile_btn.setEnabled(False)
        self.flash_btn.setEnabled(False)
        self.erase_btn.setEnabled(False)

        main = self.window()
        logger = self.logger
        yaml_path = main.get_or_create_yaml_path()

        try:
            build_name = Path(yaml_path).stem
            firmware_path = Path(".esphome") / "build" / build_name / ".pioenvs" / build_name / "firmware.bin"
            if firmware_path.exists():
                logger.log(f"📦 Firmware selezionato per l'upload: {firmware_path.resolve()}", "info")
            else:
                logger.log("⚠️ Firmware non trovato. Verrà rigenerato o non ancora compilato.", "warning")
        except Exception as ex:
            logger.log(f"⚠️ Errore durante la determinazione del binario: {ex}", "warning")

        com_port = self.com_combo.currentData() or self.com_combo.currentText()
        if not com_port:
            logger.log("❌ Nessuna porta COM selezionata.", "error")
            return

        self.compiler.log_callback = logger.log
        self.compiler.upload_via_usb(yaml_path, com_port)

    def scan_network_for_esp(self):
        """
        @brief Scans the local network for ESPHome devices listening on UDP port 3232.

        Sends a UDP broadcast and listens for replies within a timeout,
        populates the IP combo box with discovered devices and logs status.
        """
        self.logger.log(Translator.tr("scan_in_progress"), "info")
        self.ip_combo.clear()
        found_ips = []

        def scanner():
            udp_port = 3232
            message = b'ESPHomeDiscovery'
            timeout = 2

            # Invia un pacchetto broadcast UDP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(timeout)
            try:
                s.sendto(message, ('<broadcast>', udp_port))
                # Attendi le risposte
                start = socket.getdefaulttimeout()
                s.settimeout(1)
                try:
                    while True:
                        data, addr = s.recvfrom(1024)
                        ip = addr[0]
                        if ip not in found_ips:
                            found_ips.append(ip)
                            self.logger.log(Translator.tr("device_found").format(ip=ip), "success")
                            # Aggiorna la combo (thread-safe)
                            self.ip_combo.addItem(ip)
                except socket.timeout:
                    pass
            except Exception as e:
                self.logger.log(f"Errore scansione: {e}", "error")
            finally:
                s.close()
            if not found_ips:
                self.logger.log(Translator.tr("no_device_found"), "warning")
            else:
                self.logger.log(Translator.tr("devices_found").format(n=len(found_ips)), "success")

        threading.Thread(target=scanner, daemon=True).start()

    def on_combo_ip_selected(self, idx):
        """
        @brief Updates OTA IP field when an IP is selected from the combo box.

        @param idx Index of selected combo box entry.
        """
        if idx >= 0:
            ip = self.ip_combo.currentText()
            if ip:
                self.ota_ip_edit.setText(ip)

    def test_ota_connection(self):
        """
        @brief Tests connectivity to the ESP device over OTA.

        Attempts TCP connection to specified IP and port, logging success or failure.
        """
        ip = self.ota_ip_edit.text().strip()
        port = int(self.ota_port_edit.text().strip() or "3232")
        if not ip:
            self.logger.log(Translator.tr("enter_ip_warning"), "warning")
            return

        import socket
        try:
            sock = socket.create_connection((ip, port), timeout=2)
            sock.close()
            self.logger.log(Translator.tr("ota_success").format(ip=ip, port=port), "success")
        except Exception as e:
            self.logger.log(Translator.tr("ota_fail").format(ip=ip, port=port, e=e), "error")
                
    def flash_via_ota(self):
        """
        @brief Initiates OTA firmware upload.

        Logs the attempt with IP, port, and presence of password.
        """
        ip = self.ota_ip_edit.text().strip()
        port = self.ota_port_edit.text().strip()
        pwd = self.ota_pwd_edit.text()
        self.logger.log(Translator.tr("ota_upload").format(ip=ip, port=port, pwd='[inserted]' if pwd else '[empty]'), "info")
        
    def flash_via_usb(self):
        """
        @brief Stub method placeholder for USB flashing (logic to be implemented).
        """
        com = self.com_combo.currentData()
        baud = self.baud_combo.currentText()
        self.logger.log(Translator.tr("usb_upload").format(com=com, baud=baud), "info")     

    def aggiorna_label(self):
        """
        @brief Updates all UI element texts to match current language settings.

        Includes group titles, button labels, and placeholders.
        """
        # USB/Serial Loader
        self.usb_box.setTitle(Translator.tr("usb_serial_loader"))
        # Non c'è self.test_btn
        self.flash_btn.setText("📤 " + Translator.tr("upload"))
        self.erase_btn.setText("🧹 " + Translator.tr("erase_flash"))
        self.baud_combo.setItemText(0, Translator.tr("baud"))  # Solo se vuoi tradurre le voci combo
        # OTA
        self.ota_box.setTitle(Translator.tr("ota_wifi"))
        self.scan_btn.setText(Translator.tr("scan_network"))
        self.test_ota_btn.setText(Translator.tr("test_connection"))
        self.flash_ota_btn.setText(Translator.tr("flash_ota"))
        # Compilazione
        self.group_compile.setTitle(Translator.tr("firmware_compile"))
        self.compile_btn.setText("🚀 " + Translator.tr("compile"))
        # Placeholder degli edit
        self.ota_ip_edit.setPlaceholderText(Translator.tr("ip_address"))
        self.ota_port_edit.setPlaceholderText(Translator.tr("ota_port"))
        self.ota_pwd_edit.setPlaceholderText(Translator.tr("ota_password"))

    def compila_progetto(self):
        """
        @brief Initiates the compilation process for the current YAML project.

        Prevents multiple simultaneous operations by disabling buttons and setting a busy flag.
        Logs the compilation start and triggers the compiler’s compile method.
        """
        if self.busy:
            logger.debug("DEBUG: comando compile ignorato perché busy = True")
            return

        self.logger.log("────────── 🚀 COMPILAZIONE ──────────", "info")

        self.busy = True
        self.compile_btn.setEnabled(False)
        self.flash_btn.setEnabled(False)
        self.erase_btn.setEnabled(False)

        yaml_path = self.window().get_or_create_yaml_path()
        self.compiler.log_callback = self.logger.log
        self.compiler.compile_yaml(yaml_path)

    def erase_flash(self):
        """
        @brief Erases the flash memory of the connected ESP device via esptool.

        Ensures no operations are currently running, disables buttons,
        logs start and success messages, and calls the compiler’s erase method.
        """
        if self.busy:
            logger.debug("DEBUG: comando erase ignorato perché busy = True")
            return

        com_port = self.com_combo.currentData() or self.com_combo.currentText()
        if not com_port:
            self.logger.log("❌ Nessuna porta COM selezionata. Seleziona una porta per continuare.", "error")
            return

        self.logger.log("────────── 🧩 ERASE ──────────", "info")
        self.logger.log(f"🧹 Avvio cancellazione memoria su {com_port}...", "warning")

        # Blocca ulteriori operazioni
        self.busy = True
        self.flash_btn.setEnabled(False)
        self.compile_btn.setEnabled(False)
        self.erase_btn.setEnabled(False)

        # Callback di fine operazione
        def fine_erase():
            self.logger.log("✅ Memoria cancellata con successo", "success")
            self.busy = False
            self.flash_btn.setEnabled(True)
            self.compile_btn.setEnabled(True)
            self.erase_btn.setEnabled(True)

        # Lancia erase
        self.compiler.log_callback = self.logger.log
        self.compiler.on_upload_finished = fine_erase
        self.compiler.erase_flash(com_port)

    @pyqtSlot()
    def riabilita_bottoni_qt(self):
        """
        @brief Qt slot that re-enables compile, upload, and erase buttons after operations finish.

        Logs successful upload completion message and clears busy flag.
        """
        self.compile_btn.setEnabled(True)
        self.flash_btn.setEnabled(True)
        self.erase_btn.setEnabled(True)
        if "run" in (self.compiler.command if hasattr(self.compiler, "command") else []):
            self.logger.log("✅ Upload completato con successo via USB.", "success")
        self.busy = False
