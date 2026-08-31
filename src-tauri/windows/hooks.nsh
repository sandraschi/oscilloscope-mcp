; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillOscilloscopeMcpFleetProcesses
  DetailPrint "Stopping oscilloscope-mcp processes..."
  ExecWait 'taskkill /F /IM oscilloscope-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM oscilloscope-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "oscilloscope-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "oscilloscope-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "oscilloscope-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "oscilloscope-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillOscilloscopeMcpFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillOscilloscopeMcpFleetProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register oscilloscope-mcp in Cursor / Claude Desktop"
    ExecWait 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\resources\install-mcp-clients.ps1" -Interactive'
  mcp_hook_done:
!macroend
