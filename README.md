# GSM-Bayes
For the Emulators and UQ FRIB-TA summer school 2023

Our goal with this little project is to highlight some helpful features when performing Bayesian UQ using Surmise. The project uses the Gamow Shell Model code as an example but the overall approaches should be applicable to most theoretical tools.

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

Generally, before running the GSM code you would need to create a directory called "workspace" and inside this directory, make folders called "node_##" where ## coresponds to the number of nodes you'd like to use ranging from 0 to the maximum value (in the input file this is the number assigned to "MPI.processes"). An example would be 3 nodes and the terminal commands are:

$ mkdir workspace
$ mkdir workspace/node_0 workspace/node_1 workspace/node_2

**However, we've tried to make this easier on you by handling any directory creation within our python files, so if you're just running our codes, you can ignore the previous step!**

To run the GSM code given some executable file ("input.dat" for example) you may either run it in serial by:

$ ./GSM_exe <input.dat> output.dat

Or in parallel by:

$ mpirun -np 3 -map-by node -bind-to none ./GSM_exe<input.dat> output.dat

which saves the resulting outputs in "output.dat" in either case. The number of nodes i.e. "-np 3" in the parallel command above is the number of "node_##" folders you need to have made. **Again, if you're just running our python files, you can ignore this step.**

# Check your executable and template(s)

At this point, you should have a "GSM_exe" execuatble which can be copied into the GSM-Bayes directory we are going to be working in.

To make sure everything is ready to run, simply type

$ python3 exe_input_tests.py

which should produce an output similar to the following

input_5He_Mao2020.dat  runtime =  1.9152908325195312
Total runtime =  2.431422710418701

If you got an error, we're sorry, but you'll need to track it down. It likely is either an error in the default template files we are using (in the "templates" folder). A helpful debugging procedure is to run the code after copying a template file of your choice and inserting the parameters from Mao et al 2020. When you run the code with this input, it will output as it reads the file and when it encounters and error, it will tell you the line it read versus what it expected to read. If you get this error, simply provide the expected line and any parameters applicable.

# Setup runs

If your templates and execuatble are working properly, we can now setup our runs. Since our workflow is (a) run a series of high-fidelity calculations (b) build an emulator from that data and (c) perform Bayesian UQ using the emulator, we are best served having a large number of high-fidelity calculations. Since these can take a while, we recommend using a supercomputing cluster like MSU's High Performance Computing Center (HPCC). With this in mind, we've prepared the python file "run_hpcc_prep.py" which has the following arguments that can be adjusted based on your parallelization needs:
 - mpiProcesses
 - openMPthreads

These two are the number of mpi tasks and OpenMP threads which will need to be the same as in the sbatch_run.sb file.

We can run the setup script on the hpcc using:

$ python3 run_hpcc_prep.py

to generate all our high-fidelity input files to be used in emulation (created in the default folder 'emulator-runs').

# Run high-fidelity calculations

This is (hopefully) simple as all you'll need to do is modify the "sbatch_run.sb" file to have the correct mpi tasks and openMP threads usage - if you changed the setup file at all. If you did, for simplicity, make sure that the parameters:
 - #SBATCH --ntasks=mpiProcesses
 - #SBATCH --cpus-per-task=openMPthreads
 - NODES=mpiProcesses
are set accordingly.

After this optional step, simply run the sbatch file on the HPCC by:

$ sbatch sbatch_run.sb

and now you wait for the runs to finish! You can check their status any time by typing "qs" in the command line.

# Post run operations

Now we just need to collect all our data! To do so, type

$ python3 run_hpcc_post.py

which will generate a summary for the output results in a csv stored in emulator-runs. This file (and it's parameter counterpart generated with the pre-run script) are the important parts for the next step!

# Perform Bayesian Callibration

And now we're at the end - almost. You can do this next part locally if you desire. If so, be sure to copy the csv files in emulator-runs to a local folder "emulator-runs". From this point, we just need to type

$ bayesian_run.py

to make our emulator and perform Bayesian callibration with it. The output will be a corner plot showing each of our input parameters. If you'd like to do more with this, you certianly can!





