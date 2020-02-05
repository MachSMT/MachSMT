# MachSMT

This is the repo for MachSMT. 

https://sites.google.com/view/machsmt

MachSMT can be installed easily via the command `sudo python3 setup.py install` (as requirements.txt is not prepared, you may need to install a few pip3 packages). This will install two scripts:

* machsmt_select - the primary interface to MachSMT's algorithm selection
* machsmt_build  - a script to learn models for algorithm selection in MachSMT's pipeline.

# machsmt_select
The algorithm selection script can be ran with the following syntax: `machsmt_select MODEL INPUT`. MachSMT will then print the name of the solver it selects to have the shortest runtime. The models can be either built independently or prebuilt models can be downloaded [here](https://www.dropbox.com/s/hbeidctzpwilinb/lib.zip?dl=1).

# machsmt_build

To build a model for a specific logic and track, MachSMT expects acces to all benchmarks, and will look for them in the  `benchmarks/`  repository in the root of the MachSMT repo. To do so, please download logics of interest from the [SMT-LIB initiative's benchmark page](http://smtlib.cs.uiowa.edu/benchmarks.shtml), and unzip the file.

For timing analysis, please clone the [SMT-COMP's repository](https://github.com/SMT-COMP/smt-comp) in the root of the MachSMT repo, and decompress the timing analysis csv files.

Running `machsmt_build` will build models for all logics and tracks. However this can be narrowed to logics and tracks of interest by running it as `machsmt_build --logic LOGIC --track TRACK`.

The MachSMT pipeline allows for custom regression algorithms to be used, and can be easily deployed of they follow the scikit style. To modify, see `machsmt/model_maker.py`.

Further, the MachSMT pipeline strongly encourages the use of community features and can easily be added with minimal lines of code. For more, see `machsmt/extra_features.py`.

# machsmt/extra_features.py

We provide an interface for users to add extra features when building learned models for MachSMT. Extra features can be added by simply inserting python methods into the `machsmt/extra_features.py`. For more, please see the documentation in this file.

# machsmt/model_maker.py

The internall regressor within machsmt can be adjusted to any regressor that uses scikit styled syntax. 
