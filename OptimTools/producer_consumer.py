from __future__ import division, print_function
from multiprocessing import Process, Condition, Event, Queue, cpu_count
import numpy as np
import time
import random

# A Producer that initializes with loaded data then waits for further processing on that data
class _Producer(Process):
    def __init__(self, init_function, init_data, process_function, queues, conds):
        super(_Producer, self).__init__()

        self._init_fn = init_function
        self._init_dat = init_data
        self._proc_fn = process_function
        self._set_q, self._get_q = queues
        self._set_cond, self._get_cond = conds
        self._stop = Event()

    def run(self):
        # Initialize random number generators here
        random.seed()
        np.random.seed()
        # Run the initial function
        out = [self._init_fn(id) for id in self._init_dat]
        while not self._stop.is_set():
            # Pop parameters off the queue and run the process function
            self._set_cond.acquire()
            if self._set_q.empty():
                self._set_cond.wait()
                if self._stop.is_set():
                    return
            params = self._set_q.get()
            self._set_cond.release()

            # Run the function
            ret = [self._proc_fn(params, o) for o in out]

            # Put the results back onto the queue
            self._get_cond.acquire()
            self._get_q.put(ret)
            self._get_cond.notify()
            self._get_cond.release()

    def stop(self):
        self._stop.set()

# The class that will be used -- takes in initialization functions / data, slices them up, then calls a
#  process_function in a segmented way
class ProducerConsumer(object):
    def __init__(self, init_function, init_data, process_function, n_cores = cpu_count(), timeout = None):
        self._ncore = n_cores
        self._split_dat = [init_data[i::n_cores] for i in range(n_cores)]
        self._producer_list = []
        self._init_fn = init_function
        self._proc_fn = process_function
        self._timeout = timeout
        self._lastparams = None
        for i in range(n_cores):
            self._producer_list.append(self._make_producer(i))

            #set_q = Queue()
            #get_q = Queue()
            #set_cond = Condition()
            #get_cond = Condition()
            #producer = _Producer(init_function, self._split_dat[i], process_function, [set_q, get_q], [set_cond, get_cond])
            #self._producer_list.append([producer, set_q, set_cond, get_q, get_cond])
            #producer.start()

    def run(self, params):
        self._set_params(params)
        return self._get_outcomes()

    def shut_down(self):
        for p, _, c, _, _ in self._producer_list:
            c.acquire()
            p.stop()
            c.notify()
            c.release()
        self._producer_list = []

    def __del__(self):
        self.shut_down()

    def _make_producer(self, index):
        set_q = Queue()
        get_q = Queue()
        set_cond = Condition()
        get_cond = Condition()
        producer = _Producer(self._init_fn, self._split_dat[index], self._proc_fn, [set_q, get_q], [set_cond, get_cond])
        producer.start()
        return producer, set_q, set_cond, get_q, get_cond

    def _set_params(self, params):
        self._lastparams = params
        for p, q, c, _, _ in self._producer_list:
            c.acquire()
            q.put(params)
            c.notify()
            c.release()

    def _get_outcomes(self):
        starttime = time.time()
        agg = []
        for i, (p, setq, setcond, q, c) in enumerate(self._producer_list):
            c.acquire()
            if q.empty():
                if self._timeout:
                    remwait = max(self._timeout + starttime - time.time(), 1.) # Always give it a small chance to load
                    c.wait(remwait)
                    # If the queue remains empty, replace the process and try again with the last parameter set
                    while q.empty():
                        setcond.acquire()
                        p.stop()
                        setcond.notify()
                        setcond.release()
                        p.terminate()
                        print ("Process exceeded timeout limit")
                        print ("Init data:", self._split_dat[i])
                        print ("Parameters:", self._lastparams)
                        print ("Timeout:", self._timeout)
                        print ("\n")
                        pgroup = self._make_producer(i)
                        p, setq, setcond, q, c = pgroup
                        self._producer_list[i] = pgroup
                        setcond.acquire()
                        setq.put(self._lastparams)
                        setcond.notify()
                        setcond.release()
                        c.acquire()
                        if q.empty():
                            r = random.randint(0, 100)
                            print ("Start wait time:", r, time.time())
                            c.wait(self._timeout)
                            print ("End wait time:", r, time.time())
                else:
                    c.wait()
            from_q = q.get()
            agg += from_q
            c.release()
        return agg

if __name__ == '__main__':
    from scipy.stats import norm
    import random
    def initfn(s):
        print ("initialized")
        return s

    def procfn(arg, s):
        tst = 3*random.random()
        wait = s + tst
        print ("Waiting for", wait, "seconds")
        time.sleep(wait)
        return wait

    procon = ProducerConsumer(initfn, [1.,1.2,2.,1.6, 1.7], procfn, 3, timeout = 5)
    print ("Done")
    print (procon.run(2))
    del procon
