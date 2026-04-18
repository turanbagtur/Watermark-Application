[Setup]
; >>> CRÍTICO: Este AppId é o que faz o app aparecer na lista do Windows 11 <<<
AppId={{F9A8B7C6-D5E4-1234-5678-90ABCDEF1234}
AppName=Advanced Professional Watermark
AppVersion=1.0.7
AppPublisher=VENSEV
AppSupportURL=https://ko-fi.com/solderett

; Configurações de Instalação
DefaultDirName={autopf}\Advanced Professional Watermark
DefaultGroupName=Advanced Professional Watermark
OutputDir=.\InstaladorFinal
; Mudei o nome para deixar claro que este é o INSTALADOR, não o app
OutputBaseFilename=Instalar_Watermark
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\WatermarkApp.exe

; >>> CRÍTICO: Exige permissão de adm para registrar no Windows corretamente <<<
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Puxa o seu arquivo real de 12.30MB
Source: "dist\WatermarkApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Cria os atalhos reais para o app, não para o instalador
Name: "{group}\Advanced Professional Watermark"; Filename: "{app}\WatermarkApp.exe"
Name: "{group}\{cm:UninstallProgram,Advanced Professional Watermark}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Advanced Professional Watermark"; Filename: "{app}\WatermarkApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WatermarkApp.exe"; Description: "{cm:LaunchProgram,Advanced Professional Watermark}"; Flags: nowait postinstall skipifsilent