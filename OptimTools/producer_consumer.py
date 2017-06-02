from multiprocessing import Process, Condition, Event, Queue, cpu_count
import numpy as np

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
    def __init__(self, init_function, init_data, process_function, n_cores = cpu_count()):
        self._ncore = n_cores
        n_per_core = int(np.ceil(len(init_data) / n_cores))
        split_dat = [init_data[(i * n_per_core):((i + 1) * n_per_core)] for i in range(n_cores)]
        self._producer_list = []
        for i in range(n_cores):
            set_q = Queue()
            get_q = Queue()
            set_cond = Condition()
            get_cond = Condition()
            producer = _Producer(init_function, split_dat[i], process_function, [set_q, get_q], [set_cond, get_cond])
            self._producer_list.append([producer, set_q, set_cond, get_q, get_cond])
            producer.start()

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

    def _set_params(self, params):
        for p, q, c, _, _ in self._producer_list:
            c.acquire()
            q.put(params)
            c.notify()
            c.release()

    def _get_outcomes(self):
        agg = []
        for p, _, _, q, c in self._producer_list:
            c.acquire()
            if q.empty():
                c.wait()
            from_q = q.get()
            agg += from_q
            c.release()
        return agg

if __name__ == '__main__':
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
