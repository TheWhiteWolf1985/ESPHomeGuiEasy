; Script Inno Setup per ESPHomeGUIeasy v1.4.1 con collegamenti e disinstallazione

[Setup]
AppName=ESPHomeGUIeasy
AppVersion=1.4.2
DefaultDirName={autopf}\ESPHomeGUIeasy
DefaultGroupName=ESPHomeGUIeasy
OutputBaseFilename=ESPHomeGUIeasy_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=no
ShowLanguageDialog=yes
LicenseFile=license\license_en.txt
UninstallDisplayIcon={app}\esphomeguieasy.exe
UninstallDisplayName=ESPHomeGUIeasy

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "license\license_en.txt";
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"; LicenseFile: "license\license_it.txt";
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "license\license_es.txt";
Name: "german"; MessagesFile: "compiler:Languages\German.isl"; LicenseFile: "license\license_de.txt";
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"; LicenseFile: "license\license_pt.txt";

[Files]
Source: "ESPHomeGUIeasy\*"; \
  DestDir: "{app}"; \
  Flags: recursesubdirs createallsubdirs ignoreversion; \
  Excludes: "installation_utility\\user_config.db"

Source: "ESPHomeGUIeasy\user_config.db"; \
  DestDir: "{localappdata}\ESPHomeGUIeasy"; \
  Flags: ignoreversion

[Dirs]
Name: "{userdocs}\ESPHomeGUIeasy\build"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects"
Name: "{userdocs}\ESPHomeGUIeasy\community_projects"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Home_Monitoring"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Energy_Power"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Security_Alarm"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Actuators_IO"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Communication"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Automation_Logic"
Name: "{userdocs}\ESPHomeGUIeasy\user_projects\Other_Misc"

[Icons]
Name: "{group}\ESPHomeGUIeasy"; \
  Filename: "{app}\esphomeguieasy.exe"; \
  WorkingDir: "{app}"; \
  IconFilename: "{app}\assets\icon\esphomeguieasy.ico"
Name: "{commondesktop}\ESPHomeGUIeasy"; \
  Filename: "{app}\esphomeguieasy.exe"; \
  WorkingDir: "{app}"; \
  IconFilename: "{app}\assets\icon\esphomeguieasy.ico"; \
  Tasks: desktopicon
Name: "{group}\📘 Documentazione ESPHomeGUIeasy"; \
  Filename: "{app}\docs\html\index.html"; \
  WorkingDir: "{app}\docs\html"
Name: "{group}\🔻 Disinstalla ESPHomeGUIeasy"; Filename: "{uninstallexe}"
Name: "{group}\🌍 Visita il sito ufficiale"; \
  Filename: "https://github.com/TheWhiteWolf1985/ESPHomeGuiEasy"; \
  IconFilename: "{app}\assets\icon\esphomeguieasy.ico"

[Messages]
; Italiano
WelcomeLabel2=Questo installer configurerà ESPHomeGUIeasy nel tuo sistema Windows, rendendo disponibili tutte le funzionalità per la creazione, modifica e gestione dei progetti ESPHome in modalità completamente offline. Al termine dell’installazione, potrai avviare l’interfaccia, selezionare la lingua, e iniziare a creare firmware personalizzati anche senza conoscere la sintassi YAML.

[CustomMessages]
; Inglese
english_WelcomeLabel2=This installer will set up ESPHomeGUIeasy on your Windows system, enabling all features to create, edit, and manage ESPHome projects completely offline. After installation, you can launch the interface, choose your preferred language, and start building custom firmware even without writing any YAML code.

; Spagnolo
spanish_WelcomeLabel2=Este instalador configurará ESPHomeGUIeasy en tu sistema Windows, activando todas las funciones para crear, editar y gestionar proyectos de ESPHome completamente sin conexión. Al finalizar, podrás iniciar la interfaz, seleccionar tu idioma preferido y comenzar a crear firmware personalizado sin necesidad de escribir YAML.

; Tedesco
german_WelcomeLabel2=Dieses Installationsprogramm richtet ESPHomeGUIeasy auf Ihrem Windows-System ein und aktiviert alle Funktionen zur Erstellung, Bearbeitung und Verwaltung von ESPHome-Projekten im komplett Offline-Modus. Nach der Installation können Sie die Oberfläche starten, Ihre Sprache auswählen und eigene Firmware erstellen – ganz ohne YAML-Kenntnisse.

; Portoghese Brasiliano
brazilianportuguese_WelcomeLabel2=Este instalador configurará o ESPHomeGUIeasy no seu sistema Windows, ativando todos os recursos para criar, editar e gerenciar projetos ESPHome de forma totalmente offline. Após a instalação, você poderá iniciar a interface, escolher seu idioma preferido e começar a criar firmwares personalizados sem precisar escrever código YAML.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\esphomeguieasy.exe"; Description: "Avvia ESPHomeGUIeasy"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userdocs}\ESPHomeGUIeasy"

[Registry]
Root: HKCU; Subkey: "Software\ESPHomeGUIeasy"; ValueType: string; ValueName: "UserDataPath"; ValueData: "{userappdata}\ESPHomeGUIeasy"

[Code]
function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := MsgBox('Vuoi eliminare anche i progetti della community salvati in Documenti?', mbConfirmation, MB_YESNO) = IDYES;

  if Result then begin
    DelTree(ExpandConstant('{userdocs}\ESPHomeGUIeasy\community_projects'), True, True, True);
  end;

  Result := True; // Continua comunque la disinstallazione
end;


