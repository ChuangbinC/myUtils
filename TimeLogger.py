# -*- coding: utf-8 -*-
"""
本程序是用于测试python程序运行时间，来源：
https://selfboot.cn/2016/06/13/python_performance_analysis/
https://juejin.im/post/5c3b1a7bf265da6179750642

所需依赖库：
line_profiler
"""
#%%
from functools import wraps
import cProfile
from line_profiler import LineProfiler
import time

def func_time(f):
    """
    简单记录执行时间
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f.__name__, 'took', end - start, 'seconds')
        return result

    return wrapper


def func_cprofile(f):
    """
    内建分析器
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = f(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='time')

    return wrapper



try:
    from line_profiler import LineProfiler


    def func_line_time(follow=[]):
        """
        每行代码执行时间详细报告
        :param follow: 内部调用方法
        :return:
        """
        def decorate(func):
            @wraps(func)
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)
                    for f in follow:
                        profiler.add_function(f)
                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    profiler.print_stats()

            return profiled_func

        return decorate

except ImportError:
    def func_line_time(follow=[]):
        "Helpful if you accidentally leave in production!"
        def decorate(func):
            @wraps(func)
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)

            return nothing

        return decorate

"""
例程：
"""

@func_time
print('CCB')

#%%
from time import clock
class testTimer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
    def __enter__(self):
        self.start = clock()
        return self
    def __exit__(self, *args):
        self.end = clock()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)


"""
例程：
"""
with testTimer(verbose=True):
    print('CCB')
