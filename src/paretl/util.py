import time


def tim(method):
    def tm(*args, **kwargs):
        slf = args[0]
        if hasattr(slf.o, "timeit"):
            return slf.o.timeit(method, slf.o, *args, **kwargs)
        else:
            return method(*args, **kwargs)
    return tm


def timeit(method, o, *args, **kw):
    ts = time.time()
    result = method(*args, **kw)
    te = time.time()
    if 'log_time' in kw:
        name = kw.get('log_name', method.__name__.upper())
        kw['log_time'][name] = int((te - ts) * 1000)
    else:
        setattr(o, 'ms_%s_%s' % (type(args[0]).__name__, method.__name__),  (te - ts) * 1000)
    return result
