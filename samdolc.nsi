
;;; TODO
; - Conclude mongodb
; - 

!include Sections.nsh 			;UnselectSection

!define NAME "samdolc"
!define CRX_VERSION "0.1"
!define CRX_ID "onpobpkjhjihnhmjpjemcedjebllieoi"
!define BUILD_DIR "tmp\build_exe"


Name "${NAME}"

outFile "${NAME}.exe"

InstallDir $PROGRAMFILES\${NAME}

InstallDirRegKey HKLM "Software\${NAME}" "Install_Dir"

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles


Section "${NAME} (required)"

  SectionIn RO

  ; Set output path to the installation directory
  SetOutPath $INSTDIR

  File /r "${BUILD_DIR}\*.*"

  WriteRegStr HKLM SOFTWARE\${NAME} "Install_Dir" "$INSTDIR"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "DisplayName" "${NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "NoRepair" 1
  WriteUninstaller "uninstall.exe"

SectionEnd

Section "Start Menu Shortcuts"
  
  ; $SMPROGRAMS is the start programs folder.
  CreateDirectory "$SMPROGRAMS\${NAME}"
  CreateShortCut "$SMPROGRAMS\${NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

SectionEnd

Section "Install crome extention"
  WriteRegStr HKLM "Software\Google\Chrome\Extensions\${CRX_ID}" "path" "$INSTDIR\${NAME}.crx"
  WriteRegStr HKLM "Software\Google\Chrome\Extensions\${CRX_ID}" "version" "${CRX_VERSION}"
  WriteRegStr HKLM "Software\Wow6432Node\Google\Chrome\Extensions\${CRX_ID}" "path" "$INSTDIR\${NAME}.crx"
  WriteRegStr HKLM "Software\Wow6432Node\Google\Chrome\Extensions\${CRX_ID}" "version" "${CRX_VERSION}"
SectionEnd

Section "Install Samdolc as daemon"
  nsExec::Exec 'python.exe "$INSTDIR\server\samdolcd_windows.py" --startup="auto" install'
  nsExec::Exec 'python.exe "$INSTDIR\server\samdolcd_windows.py" start'
SectionEnd

Section "Install MongoDB as daemon" SEC_MONGO
  ;SetOutPath "$TEMP\${NAME}"
  CreateDirectory "$INSTDIR\data"
  nsExec::Exec '"$INSTDIR\tools\mongod.exe" --logpath "$INSTDIR\data" --dbpath "$INSTDIR\data" --install'
  nsExec::Exec 'net start Mongodb'

SectionEnd


Section "Uninstall"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"
  DeleteRegKey HKLM Software\${NAME}
  DeleteRegKey HKLM "Software\Wow6432Node\Google\Chrome\Extensions\${CRX_ID}"
  DeleteRegKey HKLM "Software\Google\Chrome\Extensions\${CRX_ID}"

  nsExec::Exec 'net stop MongoDB'
  nsExec::Exec '"$INSTDIR\tools\mongod.exe" --remove'
  nsExec::Exec 'python.exe "$INSTDIR\server\samdolcd_windows.py" stop'
  nsExec::Exec 'python.exe "$INSTDIR\server\samdolcd_windows.py" remove'

  Delete $INSTDIR\*.*
  Delete "$SMPROGRAMS\${NAME}\*.*"

  RMDir "$SMPROGRAMS\${NAME}"
  RMDir /r $INSTDIR\server
  RMDir "$INSTDIR"

SectionEnd

Function .onInit

  Exec $INSTDIR\uninstall.exe

  ; $TEMP is C:\Users\ptmono\AppData\Local\Temp
  ;CreateDirectory "$TEMP\${NAME}"

  ;!insertmacro UnselectSection ${SEC_MONGO}

 
FunctionEnd
