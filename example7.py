# Comparison of process pool and multi-process execution time
import datetime
import time
from multiprocessing import Process, Pool


def f(n):
    for i in range(50000):
        n += i
        if i == 100:
            time.sleep(3)
            # print(i)
    return i


def rudy(i):
    print(i)


if __name__ == '__main__':
    # Counting the time that the process pool is performing 100 tasks
    s_time = time.time()
    pool = Pool(4)  #This parameter is how many processes are in the specified process pool, 4 Indicates 4 processes. If you do not pass the parameters, the number of processes that are enabled by default is generally the number of cpus.
    result = pool.apply_async(f, args=(0, ), callback=rudy)
    print(result)
    # pool.map(f, range(100))  # Parameter data must be iterable, asynchronously submit tasks, from With join function
    e_time = time.time()
    dif_time = e_time - s_time

    # Count 100 processes to perform execution time for 100 tasks
    p_s_t = time.time() # Multi-process start time
    p_list = []
    for i in range(100):
        p = Process(target=f, args=(i,))
        p.start()
        print(f"[{datetime.datetime.now()}]:{p.name}")
        p_list.append(p)
    [pp.join() for pp in p_list]
    p_e_t = time.time()
    p_dif_t = p_e_t - p_s_t
    print('Process Pool Execution time: ', dif_time)
    print('Multiple processes Execution time:', p_dif_t)
