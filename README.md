# baboon-tracking
[![Build Status](https://travis-ci.org/UCSD-E4E/baboon-tracking.svg?branch=master)](https://travis-ci.org/UCSD-E4E/baboon-tracking)

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
    - [Install](#install)
    - [Lint](#lint)
    - [Run](#run)
    - [Shell](#shell)

# Contributing
## System Requirements
This project only officially runs on Ubuntu 20.04.  Other operating systems may be compatible, but are not guaranteed. We are willing to accept PRs to introduce compatibility for other operating systems, but will not be prioritizing such compatibility.

### Windows (Not officially supported)
To run the project on Windows, please ensure you run the following command in an admin PowerShell
```
Set-ExecutionPolicy Unrestricted
```

### Windows (WSL2 with Ubuntu 20.04)
This is the only supported way to run on Windows.  We do not support WSL1, only WSL2.

### Ubuntu
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
### Install
Running `./cli install` will setup up the enviornment.
### Lint
Running `./cli lint` will run `pylint`, `pyright`, and `black` to check for lint errors.
### Run
Running `./cli run` will run the algorithm and display the time of each step.
### Shell
Running `./cli shell` internally runs `./cli install` and then opens a shell in the virtual environment.

