
import signal
class TimeoutException(Exception):
    pass
def timeout_handler(signum, frame):
    raise TimeoutException
def start_with_timer_back(seconds, function, *args, **kwargs):
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(seconds) 
        return function(*args, **kwargs)
    except TimeoutException:
        print("Function timed out!")
        # input()
    finally:
        signal.alarm(0) # Disable the alarm


from multiprocessing import Process
def start_with_timer(seconds, function, *args, **kwargs):
    # We create a Process
    action_process = Process(target=function, args=args, kwargs=kwargs)

    # We start the process and we block for 5 seconds.
    action_process.start()
    action_process.join(timeout=seconds)

    # We terminate the process.
    action_process.terminate()
    print("Function timed out!")