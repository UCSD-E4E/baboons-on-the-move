using namespace System.Management.Automation.Host

function Get-Config {
    if (Test-Path ".ps-cli-config") {
        $config = Import-Clixml ".ps-cli-config"
    } else {
        $config = @{}
    }

    if ($null -eq $config["Backend"]) {
        $config.Add("Backend", (Get-BackendVersion))
    }

    $config | Set-Config
    $config
}

function Set-Config {
    Param (
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        $Config
    )

    $Config | Export-Clixml -Path ".ps-cli-config"
}

function New-WslVagrantMenu {
    $title = "WSL or Vagrant?"
    $question = "WSL provides a more performant/featureful environment for development than Vagrant does, but may block access to other virtualization or emulation platforms that depend on CPU virtualization technology.  What platform do you want to use?"
    
    $wsl = [ChoiceDescription]::new('&WSL', 'Use WSL2 with Ubuntu 20.04')
    $vagrant = [ChoiceDescription]::new('&Vagrant', 'Use Vagrant and VirtualBox with Ubuntu 20.04')

    $options = [ChoiceDescription[]]($wsl, $vagrant)

    $result = $host.ui.PromptForChoice($title, $question, $options, 0)

    switch ($result) {
        0 { "WSL2" }
        1 { "Vagrant" }
    }
}

function Get-BackendVersion {
    $windowsVersion = [System.Environment]::OSVersion.Version
    $wsl2Supported = $windowsVersion.Major -eq 10 -and $windowsVersion.Build -ge 18362

    if ($wsl2Supported) {
        New-WslVagrantMenu
    } else {
        "Vagrant"
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
        [Parameter(ValueFromPipeline = $True)]
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

function ConvertTo-LF {
    param (
        [Parameter(ValueFromPipeline = $True)]
        $Path
    )

    PROCESS {
        $Path = Resolve-Path $Path

        $text = [IO.File]::ReadAllText($Path) -replace "`r`n", "`n"
        [IO.File]::WriteAllText($Path, $text)
    }
}

function Install-Chocolatey {
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
}

function Repair-WSLOuptut {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$Output
    )

    foreach ($line in $Output) {
        $results = $line | ForEach-Object { $_.ToCharArray() | Where-Object { [int]$_ } }

        if ($null -ne $results) {
            [string]::Join("", $results)
        }
    }
}

function Install-Wsl {
    $needsRestart = $false

    where.exe wsl 1> $null 2>&1
    if (-not $?) {
        if (Test-Administrator) {
            dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

            $needsRestart = $true
        } else {
            # Restart PowerShell as Admin
            Restart-ScriptAdministrator
            Import-Path
        }
    }

    $wslVersion = [int]::Parse((Repair-WSLOuptut -Output (wsl --status) | Where-Object { $_.Contains("Default Version") } | ForEach-Object { $_.Replace("Default Version: ", "") }))
    if ($wslVersion -ne 2) {
        if (Test-Administrator) {
            if (-not ((Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform).State)) {
                dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

                $needsRestart = $true
            }

            if ($needsRestart) {
                Write-Host 'Your computer needs to restart.'
                Write-Host -NoNewLine 'Press any key to restart now...'
                $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

                Restart-Computer
            }

            wsl --set-default-version 2
        } else {
            # Restart PowerShell as Admin
            Restart-ScriptAdministrator
            Import-Path
        }
    }
}

function Install-WslUbuntu {
    $ubuntuWSL = Repair-WSLOuptut -Output (wsl -l -v) | Where-Object { $_.Contains("Ubuntu-20.04") }

    if ($null -ne $ubuntuWSL) {
        $ubuntuCurrentWSLVersion = [int]($ubuntuWSL | ForEach-Object { $_.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries) })[3]

        if ($ubuntuCurrentWSLVersion -eq 2) {
            return # Nothing to do
        } elseif ($ubuntuCurrentWSLVersion -eq 1) {
            Write-Error "Not compatible with WSL1.  Please manually upgrade your Ubuntu 20.04 machine to WSL2 and try again."

            exit
        }
    }

    if (-not (Test-Path tools)) {
        New-Item -Name tools -ItemType Directory | Out-Null
    }

    Invoke-WebRequest -Uri https://aka.ms/wslubuntu2004 -OutFile .\tools\Ubuntu.apx -UseBasicParsing
    Add-AppPackage .\tools\Ubuntu.apx
}

Push-Location $PSScriptRoot
Add-Type -AssemblyName System.Windows.Forms

$config = Get-Config

Install-Chocolatey

if ($config["Backend"] -eq "Vagrant") {
    "vagrant", "virtualbox" | Install-Package
} elseif ($config["Backend"] -eq "WSL2") {
    Install-Wsl
    Install-WslUbuntu
}

"vcxsrv" | Install-Package
"cli", "cli-mac", "cli-linux" | ConvertTo-LF

Import-Path

# Start XServer
if ($null -eq (Get-Process | Where-Object { 'vcxsrv' -eq $_.Name } )) {
    if ($config["Backend"] -eq "Vagrant") {
        & "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
    } elseif ($config["Backend"] -eq "WSL2") {
        & "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
    }
}

$screens = [System.Windows.Forms.Screen]::AllScreens
$pixels = $screens | ForEach-Object { $_.WorkingArea.Width * $_.WorkingArea.Height } | Sort-Object -Descending | Select-Object -First 1
$smallestScreen = $screens | Where-Object { $pixels -eq ($_.WorkingArea.Width * $_.WorkingArea.Height) } | Select-Object -First 1

if ($config["Backend"] -eq "Vagrant") {
    $memory = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum).Sum / 1mb
    $vagrantMemory = [System.Math]::Ceiling($memory * 0.6)

    $cpus = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
    $vagrantCpus = $cpus / 2

    $vagrantCustomFile = @"
vb:
cpus: CPUS
memory: RAM
"@
    $vagrantCustomFile = $vagrantCustomFile.Replace('CPUS', "$vagrantCpus")
    $vagrantCustomFile = $vagrantCustomFile.Replace('RAM', "$vagrantMemory")

    Set-Content -Path ./env.yml -Value $vagrantCustomFile

    $virtualBoxIpAddress = ((Get-NetIPAddress -InterfaceIndex (Get-NetAdapter | Where-Object { $_.InterfaceDescription.Contains("VirtualBox") }).ifIndex) | Where-Object { $_.AddressFamily -eq "IPv4" }).IPAddress

    if ($null -eq (vagrant status | Where-Object { $_.Contains("running") })) {
        vagrant up
    }

    vagrant -Y ssh -- -t "export DISPLAY=$($virtualBoxIpAddress):0.0; export WIDTH=$($smallestScreen.WorkingArea.Width); export HEIGHT=$($smallestScreen.WorkingArea.Height); cd /baboon-tracking; ./cli $($args[0])"

    if ($null -eq (Get-Process | Where-Object { 'vagrant' -eq $_.Name } )) {
        vagrant suspend
    }
} elseif ($config["Backend"] -eq "WSL2") {
    bash -c "export DISPLAY=`$(ip route|awk '/^default/{print `$3}'):0.0; export WIDTH=$($smallestScreen.WorkingArea.Width); export HEIGHT=$($smallestScreen.WorkingArea.Height); ./cli $($args[0])"
}
