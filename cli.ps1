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
    Start-Process powershell.exe -Verb runAs -ArgumentList "-File `"$PSCommandPath`"" -Wait -WorkingDirectory $PWD.Path
}

function Import-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User") + ";$env:APPDATA\Python\Python38\Scripts;$env:USERPROFILE\.local\bin"
}

function Install-Package {
    param(
        [Parameter(ValueFromPipeline=$True)]
        $PackageName
    )

    PROCESS {
        if ($null -eq (choco list --local-only | Where-Object { $_.Contains($PackageName) })) {
            if (Test-Administrator) {
                # Install the package
                choco install $PackageName -y
            }
            else {
                Restart-ScriptAdministrator
                Import-Path
            }
        }
    }
}

Push-Location $PSScriptRoot

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

"vagrant", "virtualbox", "vcxsrv" | Install-Package

Import-Path

if ($null -eq (Get-Process vcxsrv)) {
    & "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
}

if ("true" -eq (git config core.autocrlf)) {
    # Update line endings
    git config core.autocrlf false
    git add --renormalize .
    git reset --hard HEAD
}

$memory = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum).Sum / 1mb
$vagrantMemory = [System.Math]::Ceiling($memory * 0.6)

$vagrantCustomFile = @"
config.vm.provider :virtualbox do |v|
  v.customize ["modifyvm", :id, "--memory", 2048]
end
"@
$vagrantCustomFile = $vagrantCustomFile.Replace('2048', "$vagrantMemory")

Set-Content -Path ./Customfile -Value $vagrantCustomFile

vagrant up
vagrant -Y ssh -- -t "cd /baboon-tracking; ./cli $($args[0])"
vagrant suspend
