[Setup]
AppName=Marsis Playlist Generator
AppVersion=1.2
SetupIconFile=icon.ico
DefaultDirName={autopf}\Marsis Playlist Generator
DefaultGroupName=Marsis Playlist Generator
OutputDir=.
OutputBaseFilename=Marsis_Playlist_Generator_Setup_v12
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\gui\gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\gui\replacements.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "dist\gui\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Marsis Playlist Generator"; Filename: "{app}\gui.exe"
Name: "{autodesktop}\Marsis Playlist Generator"; Filename: "{app}\gui.exe"

[Run]
Filename: "{app}\gui.exe"; Description: "Launch Marsis Playlist Generator"; Flags: nowait postinstall skipifsilent
