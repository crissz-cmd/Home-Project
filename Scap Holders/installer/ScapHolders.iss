#define MyAppName "Scap Holders"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Christian Nathanael Susanto"
#define MyAppExeName "ScapHolders.exe"
[Setup]
AppId={{7A1B4F4D-0D1A-4D7A-9F6D-2C5D5F5E5A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Scap Holders
DefaultGroupName=Scap Holders
OutputDir=..\dist\installer
OutputBaseFilename=ScapHolders-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
[Files]
Source: "..\dist\ScapHolders\ScapHolders.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\Scap Holders"; Filename: "{app}\ScapHolders.exe"
Name: "{autodesktop}\Scap Holders"; Filename: "{app}\ScapHolders.exe"
[Run]
Filename: "{app}\ScapHolders.exe"; Description: "Launch Scap Holders"; Flags: nowait postinstall skipifsilent
