from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QLabel, QComboBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt
import socket
import threading
import serial.tools.list_ports  # Richiede pyserial
from PyQt6.QtGui import QPalette, QColor
from gui.color_pantone import Pantone

class TabCommand(QWidget):
    def __init__(self, yaml_editor, logger, compiler, flash_callback=None, ota_callback=None):
        super().__init__()
        self.yaml_editor = yaml_editor
        self.logger = logger
        self.compiler = compiler

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#3a9dda"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2a2d2e"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))

        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)           

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Sezione USB / Serial Loader (layout verticale e allineato) ---
        usb_box = QGroupBox("USB / Serial Loader")
        usb_vlayout = QVBoxLayout()

        usb_form = QFormLayout()
        usb_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        usb_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        # Baud rate
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "57600", "115200", "230400", "460800", "921600"])
        self.baud_combo.setCurrentText("115200")
        self.baud_combo.setFixedWidth(120)
        usb_form.addRow("Baud:", self.baud_combo)

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
        usb_form.addRow("Porta:", com_row)

        usb_vlayout.addLayout(usb_form)

        # Riga bottoni azione
        usb_btn_row = QHBoxLayout()
        self.test_btn = QPushButton("🔌 Test connessione")
        self.test_btn.setFixedWidth(170)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #DCDCAA;
                color: #1e1e1e;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #B1A91B;
            }
        """)
        self.flash_btn = QPushButton("💾 Carica via USB")
        self.flash_btn.setFixedWidth(170)
        self.flash_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A9955;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4e7d44;
            }
        """)

        refresh_btn.clicked.connect(self.refresh_com_ports)
        self.test_btn.clicked.connect(self.test_usb_connection)
        self.flash_btn.clicked.connect(self.flash_via_usb)


        usb_btn_row.addWidget(self.test_btn)
        usb_btn_row.addWidget(self.flash_btn)
        usb_btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usb_vlayout.addLayout(usb_btn_row)

        usb_box.setLayout(usb_vlayout)
        layout.addWidget(usb_box)


        # --- Sezione OTA (WiFi, layout verticale e allineato) ---
        ota_box = QGroupBox("OTA (WiFi)")
        ota_vlayout = QVBoxLayout()

        # Riga 1: Scansione + combo IP trovati
        scan_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 Scansiona Rete")
        self.scan_btn.setFixedWidth(160)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a9dda;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2277aa;
            }
        """)
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
        ota_form.addRow("Indirizzo IP:", self.ota_ip_edit)

        self.ota_port_edit = QLineEdit()
        self.ota_port_edit.setText("3232")
        self.ota_port_edit.setFixedWidth(80)
        ota_form.addRow("Porta:", self.ota_port_edit)

        self.ota_pwd_edit = QLineEdit()
        self.ota_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.ota_pwd_edit.setFixedWidth(230)
        ota_form.addRow("Password OTA:", self.ota_pwd_edit)

        ota_vlayout.addLayout(ota_form)

        # Riga bottoni finali (Test/Carica)
        ota_btn_row = QHBoxLayout()
        self.test_ota_btn = QPushButton("📶 Test connessione")
        self.test_ota_btn.setFixedWidth(170)
        self.test_ota_btn.setStyleSheet("""
            QPushButton {
                background-color: #DCDCAA;
                color: #1e1e1e;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #B1A91B;
            }
        """)
        self.flash_ota_btn = QPushButton("📡 Carica via OTA")
        self.flash_ota_btn.setFixedWidth(170)
        self.flash_ota_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A9955;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4e7d44;
            }
        """)

        self.scan_btn.clicked.connect(self.scan_network_for_esp)
        self.ip_combo.currentIndexChanged.connect(self.on_combo_ip_selected)
        self.test_ota_btn.clicked.connect(self.test_ota_connection)
        self.flash_ota_btn.clicked.connect(self.flash_via_ota)

        ota_btn_row.addWidget(self.test_ota_btn)
        ota_btn_row.addWidget(self.flash_ota_btn)
        ota_btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ota_vlayout.addLayout(ota_btn_row)

        ota_box.setLayout(ota_vlayout)
        layout.addWidget(ota_box)

        # --- SEZIONE COMPILAZIONE ---
        group_compile = QGroupBox("Compilazione Firmware")
        group_layout = QVBoxLayout()

        self.compile_btn = QPushButton("🚀 Compila")
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a9dda;
                color: white;
                border-radius: 8px;
                font-size: 13pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2277aa;
            }
        """)
        self.compile_btn.setFixedWidth(200)
        self.compile_btn.clicked.connect(self.compila_progetto)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.addWidget(self.compile_btn)
        group_layout.addLayout(btn_layout)
        group_compile.setLayout(group_layout)
        layout.addWidget(group_compile)

        usb_box.setStyleSheet(Pantone.GROUPBOX_STYLE)
        ota_box.setStyleSheet(Pantone.GROUPBOX_STYLE)
        group_compile.setStyleSheet(Pantone.GROUPBOX_STYLE)    

    def refresh_com_ports(self):
        """Aggiorna la lista delle porte seriali disponibili."""
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_combo.addItem(f"{port.device} ({port.description})", port.device)
        if not ports:
            self.com_combo.addItem("Nessuna porta trovata", "")

    def compila_progetto(self):
        """Compila il contenuto YAML dell'editor corrente tramite ESPHome."""
        yaml_content = self.yaml_editor.toPlainText()
        if not yaml_content.strip():
            self.logger.log("⚠️ Nessun contenuto YAML da compilare.")
            return
        self.compiler.compile_yaml(yaml_content)

    def scan_network_for_esp(self):
        """Scansiona la rete locale per trovare ESPHome in ascolto sulla porta 3232."""
        self.logger.log("🔎 Scansione rete locale in corso (broadcast UDP su 3232)...", "info")
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
                            self.logger.log(f"🎯 Dispositivo trovato: {ip}", "success")
                            # Aggiorna la combo (thread-safe)
                            self.ip_combo.addItem(ip)
                except socket.timeout:
                    pass
            except Exception as e:
                self.logger.log(f"Errore scansione: {e}", "error")
            finally:
                s.close()
            if not found_ips:
                self.logger.log("❌ Nessun dispositivo ESPHome trovato sulla rete.", "warning")
            else:
                self.logger.log(f"✅ Trovati {len(found_ips)} dispositivi.", "success")

        threading.Thread(target=scanner, daemon=True).start()

    def on_combo_ip_selected(self, idx):
        if idx >= 0:
            ip = self.ip_combo.currentText()
            if ip:
                self.ota_ip_edit.setText(ip)

    def test_ota_connection(self):
        ip = self.ota_ip_edit.text().strip()
        port = int(self.ota_port_edit.text().strip() or "3232")
        if not ip:
            self.logger.log("⚠️ Inserisci un indirizzo IP per il test.", "warning")
            return

        import socket
        try:
            sock = socket.create_connection((ip, port), timeout=2)
            sock.close()
            self.logger.log(f"✅ Il dispositivo {ip}:{port} risponde!", "success")
        except Exception as e:
            self.logger.log(f"❌ Connessione fallita verso {ip}:{port} ({e})", "error")
                
    def flash_via_ota(self):
        ip = self.ota_ip_edit.text().strip()
        port = self.ota_port_edit.text().strip()
        pwd = self.ota_pwd_edit.text()
        self.logger.log(f"🚀 Caricamento OTA su {ip}:{port} con password {'[inserita]' if pwd else '[vuota]'} (implementazione in arrivo!)", "info")
        
    def test_usb_connection(self):
        """Stub per test USB: da completare con la logica vera."""
        com = self.com_combo.currentData()
        baud = self.baud_combo.currentText()
        if not com:
            self.logger.log("⚠️ Nessuna porta seriale selezionata!", "warning")
            return
        self.logger.log(f"Test connessione su {com} @ {baud} baud (implementazione da fare)", "info")

    def flash_via_usb(self):
        """Stub per flash USB: da completare con la logica vera."""
        com = self.com_combo.currentData()
        baud = self.baud_combo.currentText()
        self.logger.log(f"Caricamento firmware via USB su {com} @ {baud} baud (implementazione da fare)", "info")        