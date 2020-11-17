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

Push-Location $PSScriptRoot
Add-Type -AssemblyName System.Windows.Forms

if ('true' -eq (git config core.autocrlf)) {
    git config core.eol lf
    git config core.autocrlf input

    git checkout-index --force --all # Rebuild working dir with all text files corrected
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

"vagrant", "virtualbox", "vcxsrv" | Install-Package

Import-Path

# Start XServer
if ($null -eq (Get-Process | Where-Object { 'vcxsrv' -eq $_.Name } )) {
    & "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
}

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

$screens = [System.Windows.Forms.Screen]::AllScreens
$pixels = $screens | ForEach-Object { $_.WorkingArea.Width * $_.WorkingArea.Height } | Sort-Object -Descending | Select-Object -First 1
$smallestScreen = $screens | Where-Object { $pixels -eq ($_.WorkingArea.Width * $_.WorkingArea.Height) } | Select-Object -First 1

if ($null -eq (vagrant status | Where-Object { $_.Contains("running") })) {
    vagrant up
}

vagrant -Y ssh -- -t "export DISPLAY=$($virtualBoxIpAddress):0.0; export WIDTH=$($smallestScreen.WorkingArea.Width); export HEIGHT=$($smallestScreen.WorkingArea.Height); cd /baboon-tracking; ./cli $($args[0])"

if ($null -eq (Get-Process | Where-Object { 'vagrant' -eq $_.Name } )) {
    vagrant suspend
}
