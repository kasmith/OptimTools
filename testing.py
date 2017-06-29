from OptimTools import *
import numpy as np
from scipy.stats import norm
import os

###########
#
# SPSA tests
#
###########

nruns = 0
if os.path.isfile('tmpstate.json'):
    os.remove('tmpstate.json')

def rosenbrock_test_fun(params):
    r = 0
    for i in range(len(params)-1):
        infnc = params[i+1] - params[i]*params[i]
        r += 100*infnc*infnc + (params[i]-1)*(params[i]-1)
    r += norm.rvs(loc=0,scale=1,size=1)
    return r

def failure_test_fun(params):
    global nruns
    nruns += 1
    if nruns == 100:
        raise Exception('Hahaha')
    return rosenbrock_test_fun(params)

# Run SPSA normally
ipars = [1.2, 3.4, -5.2, 10.8]
print "Normal SPSA"
o, _, _ = SPSA(rosenbrock_test_fun, ipars, maxiter=200, print_iters=10)
print o

# Run with a midway crash
print "\n\nCrash SPSA"
try:
    o, _, _ = SPSA(failure_test_fun, ipars, maxiter=200, print_iters=10, savestate="tmpstate.json")
except:
    print "\n\nFirst try failed"

o, _, _ = SPSA(failure_test_fun, ipars, maxiter=200, print_iters=10, savestate="tmpstate.json")
print o