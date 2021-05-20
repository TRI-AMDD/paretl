"""Functions for timing of method calls.

"""
import time


def tim(method):
    """
    Decorator to time a method call of an ETL if its output object supports it

    Arguments:
        method (function) the method to time
    """
    def tm(*args, **kwargs):
        slf = args[0]
        if hasattr(slf.o, "timeit"):
            return slf.o.timeit(method, slf.o, *args, **kwargs)
        else:
            return method(*args, **kwargs)
    return tm


def timeit(method, o, *args, **kw):
    """
    Time a method call

    Arguments:
        method (function) the method to time
        o (object) the output to add the result to
        *args forward remaing arguments to method
        *kw forward keyword argument to method
    """
    ts = time.time()
    result = method(*args, **kw)
    te = time.time()
    delta = int((te - ts) * 1000)
    if 'log_time' in kw:
        # explicit structuring of timings
        name = kw.get('log_name', method.__name__.upper())
        kw['log_time'][name] = delta
    else:
        # simple naming scheme: ms_class_method
        setattr(o, 'ms_%s_%s' % (type(args[0]).__name__, method.__name__),  delta)
    return result
