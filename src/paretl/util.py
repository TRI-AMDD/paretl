"""Functions for timing of method calls.

"""
import time


def tim(method):
    """
    Decorator to time a method call of an ETL if its output object supports it

    Args:
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

    Args:
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


def compress(value, ndarray, array, modf):
    """
    Compact data types of arrays before saving output
    """
    if isinstance(value, ndarray):
        dtype = value.dtype
        dt = dtype.str[1:]
        if dtype.kind in ['i', 'u'] or (dt in ['f2', 'f4', 'f8'] and abs(modf(value)[0]).sum() == 0):
            a, b = value.min(), value.max()
            if a >= 0 and b < 2**1:
                dt = 'b1'
            elif a >= 0 and b < 2**8:
                dt = 'u1'
            elif a > -2**7 and b < 2**7:
                dt = 'i1'
            elif a >= 0 and b < 2**16 and dt not in ['f2']:
                dt = 'u2'
            elif a > -2**15 and b < 2**15 and dt not in ['f2']:
                dt = 'i2'
            elif a >= 0 and b < 2**32 and dt not in ['f2', 'f4']:
                dt = 'u4'
            elif a > -2**31 and b < 2**31 and dt not in ['f2', 'f4']:
                dt = 'i4'
        if dt != dtype.str[1:]:
            value = array(value, dtype=dt)
    return value
