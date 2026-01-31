Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Rafi7\Downloads\Ai Training Agent\kaggle-monitor"
WshShell.Run "python remote_starter.py", 0, False
Set WshShell = Nothing
