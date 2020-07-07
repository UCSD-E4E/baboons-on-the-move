function Set-ConsoleColor {
    param (
        [Parameter(Position=0)]
        [string]$Color
    )

    if (($IsWindows -or $null -eq $IsWindows) -and $env:TERM_PROGRAM -ne 'vscode') {
        cmd /c color $Color
    }
}

Set-ConsoleColor 09

python ./cli.py $args[0]

if ($args[0] -eq "shell") {
    Set-ConsoleColor 5f
}