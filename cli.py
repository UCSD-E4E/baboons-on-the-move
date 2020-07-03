import argparse
import glob
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Baboon Command Line Interface')

    subparsers = parser.add_subparsers()

    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)

    lint_parser = subparsers.add_parser('lint')
    lint_parser.set_defaults(func=lint)

    vscode_parser = subparsers.add_parser('vscode')
    vscode_parser.set_defaults(func=vscode)

    res = parser.parse_args()

    res.func()

def _ensure_vscode_plugin(plugin: str):
    with os.popen('code --list-extensions') as f:
        installed = any([l.strip() == plugin for l in f.readlines()])

    if not installed:
        os.popen('code --install-extension ' + plugin)

def _get_node_executable(name: str):
    if sys.platform == 'win32':
        return name + '.cmd'
    elif sys.platform == 'darwin' or sys.platform == 'linux' or sys.platform == 'linux2':
        return name

def _is_executable_in_path(executable: str):
    if sys.platform == 'win32':
        whichExecutable = 'where'
    elif sys.platform == 'darwin' or sys.platform == 'linux' or sys.platform == 'linux2':
        whichExecutable = 'which'

    which = subprocess.Popen(whichExecutable + ' ' + executable, stdout = subprocess.PIPE)
    _ = which.communicate()

    return which.returncode == 0

def shell():
    if not _is_executable_in_path('poetry'):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pipx'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'install', 'poetry'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'ensurepath'])

    if not _is_executable_in_path('pyright'):
        subprocess.check_call([_get_node_executable('npm'), 'install', '-g', 'pyright'])

    subprocess.check_call(['poetry', 'install'])

    subprocess.check_call(['poetry', 'shell'])

def lint():
    from pylint.lint import Run

    repo_directory = os.path.dirname(os.path.realpath(__file__))
    python_files = [f for f in glob.iglob(repo_directory + '/**/*.py', recursive=True)]

    Run(python_files)
    subprocess.check_call(_get_node_executable('pyright'))

def vscode():
    _ensure_vscode_plugin('ms-python.python')
    _ensure_vscode_plugin('ms-python.vscode-pylance')

    os.popen('code')

if __name__ == '__main__':
    main()
