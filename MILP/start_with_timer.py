
import signal
class TimeoutException(Exception):
    pass
def timeout_handler(signum, frame):
    raise TimeoutException
def start_with_timer(seconds, function, *args, **kwargs):
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(seconds) 
        return function(*args, **kwargs)
    except TimeoutException:
        print("Function timed out!")
    finally:
        signal.alarm(0) # Disable the alarm