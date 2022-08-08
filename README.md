# baboon-tracking
[![Main Build](https://github.com/UCSD-E4E/baboon-tracking/actions/workflows/main-build.yml/badge.svg)](https://github.com/UCSD-E4E/baboon-tracking/actions/workflows/main-build.yml)

This repository contains the state-of-the-art aerial drone background tracking algorithm.  This project is sponsored by [UCSD Engineers for Exploration](http://e4e.ucsd.edu/).

- [baboon-tracking](#baboon-tracking)
- [Contributing](#contributing)
  - [System Requirements](#system-requirements)
  - [Recommended Development Enviornment](#recommended-development-enviornment)
  - [Development Procedures](#development-procedures)
  - [Commands](#commands)
    - [Chart/Flowchart](#chartflowchart)
    - [Code/VSCode](#codevscode)
    - [Data](#data)
    - [Decrypt](#decrypt)
    - [Encrypt](#encrypt)
    - [Format](#format)
    - [Lint](#lint)
    - [Run](#run)
    - [Shell](#shell)

# Contributing
## System Requirements
This project only officially runs on Ubuntu 20.04 and 22.04.  Other operating systems are compatible through the use of Vagrant.

### Windows
To run the project on Windows, please ensure you run the following command in an admin PowerShell
```
Set-ExecutionPolicy Unrestricted
```

### macOS
Please ensure you have HomeBrew installed.

### Ubuntu 22.04
To run the project on Ubuntu, please ensure you run the following command.
```
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
```

### Ubuntu 20.04
To run the project on Ubuntu, please ensure you run the following command.
```
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
```

## Recommended Development Enviornment
This repository provides some default configurations for Visual Studio Code.  In order for the default configuration to work, it is necessary to run `./cli code` at least once.  While it is possible to run this project using other tools, these configurations are not supported and YMMV.

## Development Procedures
This project leverages a CLI written in Python with bootstrappers for PowerShell and Bash.

It is recommended that as a new contributor to the project, you first run `./cli chart` and understand the flow of information through the program.

## Commands
### Chart/Flowchart
Running `./cli chart` or `./cli flowchart` will display a chart that shows each step of the execution.
### Code/VSCode
Running `./cli code` will open the installed instance of Visual Studio Code and ensure that the expected extensions are installed.
### Data
Running `./cli data` will download the data from the Team's Google Drive.
### Decrypt
Running `./cli decrypt` will ask for a password for decrypting all files in the `encrypted` folder.  It will use the `ENCRYPTION_KEY` environment variable as the password if supplied.
### Encrypt
Running `./cli encrypt` will ask for a password for encrypting all files in the `decrypted` folder.  It will use the `ENCRYPTION_KEY` environment variable as the password if supplied.
### Format
Running `./cli format` will use `black` to automatically format all of the Python scripts.
### Lint
Running `./cli lint` will run `pylint`, `pyright`, and `black` to check for lint errors.
### Run
Running `./cli run` will run the algorithm and display the time of each step.
### Shell
Running `./cli shell` internally runs `./cli install` and then opens a shell in the virtual environment.
### Docs
Running `./cli docs` will generate sphinx docs and copy to the `docs` folder, where it can be hosted on github pages.

