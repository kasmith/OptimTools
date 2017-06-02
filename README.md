# OptimTools
Python tools to make function and optimization easier

Contains three functions and one class

Functions:

1) async_map: runs like map() but does so across multiple cores

2) async_apply: applies a function to a pool in a more flexible manner than the multiprocessing pool apply

3) SPSA: runs Simultaneous Perturbation Stochastic Optimization

Class:

ProducerConsumer: segments data initialization and function running across multiple processes. Useful, for instance when you need to load or preprocess large amounts of data, and running likelihood functions is also expensive. Allows the loading/preprocessing to happen once (split across cores), while still allowing for splitting the function call across those cores.

Alternately, Pool and cpu_count can be exported, but these are simply from the multiprocessing package

To build this package, enter the directory and type:
> python setup.py build
>
> python setup.py install

Note: you may need to 'sudo' the second line

Functions async_map and apply_async are modified from http://stackoverflow.com/questions/8804830/python-multiprocessing-pickling-error

Function SPSA is modified from https://github.com/jgomezdans/spsa/blob/master/spsa/SPSA.py (certain functionality wasn't working)

ProducerConsumer is loosely based on http://agiliq.com/blog/2013/10/producer-consumer-problem-in-python/

------------ Function Definitions ----------------------

async_map(fun, args, ncpu = cpu_count())

* fun: function to run arguments over
* args: arguments to give to the function
* ncpu: the number of cores to use (defaults to all available cores)

async_apply(pool, fun, args)

* pool: a multiprocessing.Pool object
* fun: function to run arguments over
* args: arguments to give to the function

SPSA(fnc,initparams,a_par = 1e-6, c_par = .01, args = (), bounds = None, param_tol = None, ftol = 1e-8, maxiter = 10000, alpha = .602, gamma = .101, print_iters = 100.)

* fnc: function that returns a log-likelihood to stochastically minimize
* initparams: initial parameter values for the function
* a_par, c_par: control parameters
* args: other arguments to provide to the function
* bounds: a list of 2-length tuples the size of the initparams list that provide (lower,upper) bounds
* param_tol: maximum change in any parameter for an iteration
* ftol: tolerance below which optimization stops
* maxiter: maximum number of iterations to run
* alpha, gamma: more control parameters (typically set at these values)
* print_iters: number of iterations between screen output

For further information about SPSA control parameters see http://techdigest.jhuapl.edu/td/td1904/spall.pdf

ProducerConsumer(init_function, init_data, process_function, n_cores)

* init_function: the function that gets called on each piece of init_data to load or preprocess the data
* init_data: a list of data pieces that are passed to init_function individually
* process_function: a function that takes in two arguments -- a set of parameters that can vary (but will be the same across all sets of data), and the output from init_function
* n_cores: the number of process cores to use

You can call the method `run(params)` which will call the process function with those parameters to return the output from all initialized data

An example of this might be:

    from OptimTools import ProducerConsumer
    import time
    def initfn(s):
        time.sleep(s)
        print "Slept for ", s, "seconds"
        return s

    def procfn(arg, s):
        print "Adding", arg, "and",s
        return arg+s

    procon = ProducerConsumer(initfn, [1.,1.2,2.,1.6], procfn, 2)
    print "Done"
    print procon.run(2)
    print procon.run(-1)