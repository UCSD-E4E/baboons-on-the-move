In this folder there are the printed runtimes for the four short test files.

Tests run on:
Ubuntu 20.04.2 LTS
Intel i5-9600k 6 cores at 4.7GHZ
16GB 3600MHZ memory

Approx difference of avg time by stage:
GenerateWeights - 55.55 ms
Foreground - 51.85 ms

conda_bench is the runtime with the conda version of Python without any cython inserted.
all runs were done with conda except for venv_bench. 

To build the cython files install cython, then run setup.py which should build the c, HTML, and executables. For now, 
the executables have to be manually moved from the build folder to the cooresponding directory of the .pyx file.