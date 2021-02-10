import os
import sys
sys.path.append(os.getcwd() + "/src")

from cli_plugins.install import install

install()
from baboon_tracking import BaboonTracker

def main():
    files = ["test1.mp4", "test2.mp4", "test3.mp4", "test4.mp4"]
    for file in files:
        print(file)
        BaboonTracker(input_file=f"tests/{file}").run()


if __name__ == "__main__":
    install()
    main()
