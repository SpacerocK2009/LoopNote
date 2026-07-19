Option Explicit

Dim shell, fileSystem, scriptDirectory, command, argument
Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

scriptDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
command = Chr(34) & scriptDirectory & "\start.bat" & Chr(34)

For Each argument In WScript.Arguments
    command = command & " " & Chr(34) & Replace(argument, Chr(34), Chr(34) & Chr(34)) & Chr(34)
Next

' Window style 0 keeps the command prompt completely hidden.
shell.Run command, 0, False
