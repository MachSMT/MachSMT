# SMTZILLA

This is the repo for SMTZILLA. 

SMTZILLA can be installed easily via the command `sudo python3 setup.py install` (as requirements.txt is not prepared, you may need to install a few pip3 packages). This will install two scripts:

* smtzilla_select - the primary interface to SMTZILLA's algorithm selection
* smtzilla_build  - a script to learn models for algorithm selection in SMTZILLA's pipeline.

# smtzilla_select
The algorithm selection script can be ran with the following syntax: `smtzilla_select --file FILE --theory THEORY --track TRACK`. SMTZILLA will then print the name of the solver it selects to have the shortest runtime. SMTZILLA presupposes a `lib/` directory created by `smtzilla_build` in the root of the SMTZILLA repo. These can be built independently, but we provide ours [here](https://www.dropbox.com/s/hbeidctzpwilinb/lib.zip?dl=1).

# smtzilla_build

To build a model for a specific theory/track, SMTZILLA expects acces to all benchmarks, and will look for them in the  `benchmarks/`  repository in the root of the SMTZILLA repo. To do so, please download theories of interest from the [SMT-LIB initiative's benchmark page](http://smtlib.cs.uiowa.edu/benchmarks.shtml), and unzip the theory's benchmarks.

For timing analysis, please clone the [SMT-COMP's repository](https://github.com/SMT-COMP/smt-comp) in the root of the SMTZILLA repo, and decompress the timing analysis csv files.

Running `smtzilla_build` will build models for all theories/tracks. However this can be narrowed to theories/tracks of interest by running it as `smtzilla_build --theory THEORY --track TRACK`
