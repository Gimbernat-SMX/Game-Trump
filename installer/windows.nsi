Unicode True
!include "MUI2.nsh"

; ---- General ----
Name "GimbernatBros"
OutFile "GimbernatBros-Installer.exe"
InstallDir "$PROGRAMFILES64\GimbernatBros"
RequestExecutionLevel admin

; ---- Páginas del instalador ----
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

; ---- Instalación ----
Section "GimbernatBros"
    SetOutPath "$INSTDIR"
    File /r "dist\GimbernatBros\*"

    ; Accesos directos
    CreateDirectory "$SMPROGRAMS\GimbernatBros"
    CreateShortcut "$SMPROGRAMS\GimbernatBros\GimbernatBros.lnk" "$INSTDIR\GimbernatBros.exe"
    CreateShortcut "$DESKTOP\GimbernatBros.lnk" "$INSTDIR\GimbernatBros.exe"

    ; Registro para desinstalar
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GimbernatBros" \
        "DisplayName" "GimbernatBros"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GimbernatBros" \
        "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GimbernatBros" \
        "DisplayVersion" "1.0"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; ---- Desinstalación ----
Section "Uninstall"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\GimbernatBros.lnk"
    Delete "$SMPROGRAMS\GimbernatBros\GimbernatBros.lnk"
    RMDir  "$SMPROGRAMS\GimbernatBros"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GimbernatBros"
SectionEnd
