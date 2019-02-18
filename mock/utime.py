import time as _time


def localtime(*args, **kwarg):
    pass


def sleep(sec):
    _time.sleep(int(sec))


def sleep_ms(msec):
    _time.sleep(msec / 1000)


def time(*args, **kwarg):
    return int(_time.time())


def ticks_ms(*args, **kwarg):
    return int(_time.time() % 1 * 1000)


def mktime(*args, **kwarg):
    pass
