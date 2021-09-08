# baboon-tracking
This repository contains the C++ implementation of a state-of-the-art aerial drone background subtraction and object tracking algorithm.  This project is sponsored by [UCSD Engineers for Exploration](http://e4e.ucsd.edu/).

- [baboon-tracking](#baboon-tracking)
- [Contributing](#contributing)
  - [System Requirements](#system-requirements)
  - [Recommended Development Enviornment](#recommended-development-enviornment)
  - [Development Procedures](#development-procedures)

# Contributing
## System Requirements
This project has only been tested on Ubuntu 18.04 (Bionic Beaver) and Arch Linux.

It is designed to be portable and compatible with any platform that can install (or build) OpenCV 4.\* and build C++17 code with CMake, but it has not been tested and is not guranteed to work without some build system modifications on macOS and Windows or other platforms.

### Ubuntu
The project requires the following packages to be installed (or their equivalents built manually and installed system-wide):
```
 # apt install -y cmake gcc-8 g++-8 build-essential libopencv-dev
```

If you want to use the built-in CUDA acceleration you should build OpenCV yourself with CUDA enabled.

This installs GCC 8 because it's the latest version available in the default Bionic repos, but any later version of GCC should work. The project is tested and designed to build with Clang 10+ as well.

### Arch Linux
The project requires the following packages to be installed (or their equivalents build manually and installed system-wide):
```
 # pacman -Syu make cmake gcc opencv
```

If you want to use the built-in CUDA acceleration you can either use the `opencv-cuda` package available on the AUR, or you an modify the `opencv-git` package's PKGBUILD to enable CUDA support (this will also likely require the `cuda` package to be installed.)

The project is tested and designed to build with GCC 8+ (but a much newer version should be available in the Arch Linux official repos.) The project is tested and designed to build with Clang 10+ as well.
 
## Building the Project
In the `cxx` subdirectory make a `build` subdirectory to store your build files and enter the directory:
```
 $ mkdir build
 $ cd build
```

Then, configure CMake:
```
 $ cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=True
```

You should pass `-DUSE_CUDE=True` in the above step if you want to use CUDA and your system's OpenCV install was built with CUDA.

Finally, build the project with `make` (you can also tell CMake to generate build files for the Ninja build system, which may be faster):
```
 $ make -j
```


## Recommended Development Enviornment
clangd is the best way to get code completion and compilation error checking (collectively often termend 'Intellisense'.) There is a plugin for VisualStudio Code that you should use instead of the default C++ plugin. coc and coc.clangd in a new version of Vim or NVim work well if you are a Vim user. NVim also has built-in language server support that will work with clangd, but the author of this documentation hasn't tried that out so you're on your own there.

You need to do three things to use clangd.
 1. Configure CMake with the `-DCMAKE_EXPORT_COMPILE_COMMANDS=1` flag and build with Clang by setting the `CC=clang CXX=clang++` environment variables directly before the CMake command (e.g. your command will be `CC=clang CXX=clang++ cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=True`.)
 2. There should be a symbolic link to the `compile_commands.json` in your build directory already checked in. If there is not one you should make it.
 3. Start your editor in the cxx directory (we have put the `compile_commands.json` here so the editor can find it.)

If you want to debug your code you can use `gdb`. Documentation on `gdb` commands and usage is out of the scope of this document, but it is relatively straightforward to use and there are only a few commands you need to know for regular use. You may want to install the Eigen GDB plugin for `Eigen::Matrix` pretty-printing. You will want to configure CMake in Debug mode so that your binary is not stripped of debug symbols and does not have parts optimized out so that you can set breakpoints on every line. To do this you will need to rerun the command used above to configure CMake with `-DCMAKE_BUILD_TYPE=Debug`.

## Development Procedures
Before commiting your code you should format everything with `clang-format` 12 with the LLVM style. Run the following in the `cxx` directory:
```
 $ clang-format -i --style=llvm ./src/**/*.cpp ./src/**/*.h ./src/*.cpp ./src/*.h
```
