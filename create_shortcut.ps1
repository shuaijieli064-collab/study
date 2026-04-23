$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\zhixiaotong.lnk")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = "C:\Users\lsj\study\backend\app.py"
$Shortcut.WorkingDirectory = "C:\Users\lsj\study\backend"
$Shortcut.Description = "Zhixiaotong AI Assistant"
$Shortcut.Save()
Write-Host "Done!"