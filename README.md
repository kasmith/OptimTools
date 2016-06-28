# OptimTools
Python tools to make function and optimization easier

Contains three functions:

1) async_map: runs like map() but does so across multiple cores
2) async_apply: applies a function to a pool in a more flexible manner than the multiprocessing pool apply
3) SPSA: runs Simultaneous Perturbation Stochastic Optimization

Alternately, Pool and cpu_count can be exported, but these are simply from the multiprocessing package

To build this package, enter the directory and type:
> python setup.py build
> python setup.py install

Note: you may need to 'sudo' the second line

Functions async_map and apply_async are modified from http://stackoverflow.com/questions/8804830/python-multiprocessing-pickling-error

Function SPSA is modified from https://github.com/jgomezdans/spsa/blob/master/spsa/SPSA.py (certain functionality wasn't working)

------------ Function Definitions ----------------------

async_map(fun, args, ncpu = cpu_count())
    fun: function to run arguments over
    args: arguments to give to the function
    ncpu: the number of cores to use (defaults to all available cores)

async_apply(pool, fun, args)
    pool: a multiprocessing.Pool object
    fun: function to run arguments over
    args: arguments to give to the function

SPSA(fnc,initparams,a_par = 1e-6, c_par = .01, args = (), bounds = None, param_tol = None, ftol = 1e-8, maxiter = 10000, alpha = .602, gamma = .101, print_iters = 100.)
    fnc: function that returns a log-likelihood to stochastically minimize
    initparams: initial parameter values for the function
    a_par, c_par: control parameters
    args: other arguments to provide to the function
    bounds: a list of 2-length tuples the size of the initparams list that provide (lower,upper) bounds
    param_tol: maximum change in any parameter for an iteration
    ftol: tolerance below which optimization stops
    maxiter: maximum number of iterations to run
    alpha, gamma: more control parameters (typically set at these values)
    print_iters: number of iterations between screen output

For further information about SPSA control parameters see http://techdigest.jhuapl.edu/td/td1904/spall.pdf