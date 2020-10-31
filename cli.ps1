function Set-ConsoleColor {
    param (
        [Parameter(Position = 0)]
        [string]$Color
    )

    if (($IsWindows -or $null -eq $IsWindows) -and $env:TERM_PROGRAM -ne 'vscode' -and $null -eq $env:WT_PROFILE_ID) {
        cmd /c color $Color
    }
}

function Test-Administrator {  
    $user = [Security.Principal.WindowsIdentity]::GetCurrent();
    (New-Object Security.Principal.WindowsPrincipal $user).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)  
}

function Restart-ScriptAdministrator {
    Start-Process powershell.exe -Verb runAs -ArgumentList "-File `"$PSCommandPath`"" -Wait
}

function Import-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User") + ";$env:APPDATA\Python\Python38\Scripts;$env:USERPROFILE\.local\bin"
}

where.exe choco 1> $null 2>&1
if (-not $?) {
    if (Test-Administrator) {
        # Install Chocolatey
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    }
    else {
        # Restart PowerShell as Admin
        Restart-ScriptAdministrator
        Import-Path
    }
}

if ("$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python.exe" -eq (where.exe python)) {
    if (Test-Administrator) {
        # Install Python
        choco install python --version=3.8.6 -y
    }
    else {
        Restart-ScriptAdministrator
        Import-Path
    }
}

Import-Path
python ./cli.py $args[0]
