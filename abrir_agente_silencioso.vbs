Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\Projetos\agente_resumidor\abrir_agente.bat" & Chr(34), 0
Set WshShell = Nothing
