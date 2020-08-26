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
    - [Format](#format)
    - [Install](#install)
    - [Lint](#lint)
    - [Run](#run)
    - [Shell](#shell)

# Contributing
## System Requirements
This baboon tracking project should be able to run anywhere where Python 3.x is supported.

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

