; Script Inno Setup per ESPHomeGUIeasy v1.3.0 con collegamenti e disinstallazione

[Setup]
AppName=ESPHomeGUIeasy
AppVersion=1.3.0
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
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"; LicenseFile: "license\license_it.txt"
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "license\license_en.txt"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "license\license_es.txt"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"; LicenseFile: "license\license_de.txt"

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
Name: "{group}\ESPHomeGUIeasy"; Filename: "{app}\esphomeguieasy.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon\esphomeguieasy.ico"
Name: "{commondesktop}\ESPHomeGUIeasy"; Filename: "{app}\esphomeguieasy.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon\esphomeguieasy.ico"; Tasks: desktopicon

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


