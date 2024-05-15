import threading
import functools
from datetime import datetime, timedelta
from time import sleep


def get_now():
    """
    return current time to minute precision
    """
    return datetime.now().replace(second=0, microsecond=0)


def threaded(func):
    """
    wrapper to launch <func> in a new thread
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


@threaded
def set_reminder(message: str, minutes: int):
    """
    send <message> after <minutes>
    usage: threaded(remind(message,minutes))
    """
    time_now = get_now()
    future = time_now + timedelta(minutes=minutes)
    future.replace(second=0, microsecond=0)

    while True:
        if future == get_now():
            return message
        else:
            sleep(60)
