# GSM-Bayes
For the Emulators and UQ FRIB-TA summer school 2023

Use pyMC or surmise


# Where to get GSM and how to set it up

The Gamow Shell Model code can be found at the following GitHub page: https://github.com/GSMUTNSR/book_codes

This repository also contains a textbook which is a very nice explanation of the inner-workings of the theory.

Once you have cloned this repository, unzip the "GSM_code_repository.zip" file.

Navagate to the folder "GSM_code_repository/GSM_code/GSM_dir_2D/GSM_dir" and run the following commands. Note in the commands below the "$" indicates to run the subsequent commands in a terminal.

If you are working on a local desktop or laptop, run the following commands (assuming OpenMPI and GNU are on your computer):
 - $ export CC="mpic++ -fopenmp -O3 -W -Wall"
 - $ make clean
 - $ make

If you are working on MSU's HPCC, you will need to modify the runs slightly by doing:
 - $ module load GNU/7.3.0-2.30
 - $ module load OpenMPI/3.1.1
 - $ export CC="mpic++ -fopenmp -O3 -W -Wall"
 - $ make clean
 - $ make

Once running "make" has finished, there should be an executable "GSM_exe" which can now be used. Copy this executable to whatever directory you would like to work in.

Before running the GSM code, be sure to create a directory called "workspace" and inside this directory, make folders called "node_##" where ## coresponds to the number of nodes you'd like to use ranging from 0 to the maximum value (in the input file this is the number assigned to "MPI.processes"). An example would be 3 nodes and the terminal commands are:

$ mkdir workspace
$ mkdir workspace/node_0 workspace/node_1 workspace/node_2

To run the GSM code given some executable file ("input.dat" for example) you may either run it in serial by:

$ ./GSM_exe <input.dat> output.dat

Or in parallel by:

$ mpirun -np 3 -map-by node -bind-to none ./GSM_exe<input.dat> output.dat

which saves the resulting outputs in "output.dat" in either case. The number of nodes i.e. "-np 3" in the parallel command above is the number of "node_##" folders you need to have made.

