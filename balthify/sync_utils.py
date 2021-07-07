import asyncio
from concurrent.futures import Future, Executor
import functools

class BaseSafeWrapper:
    '''Accesses underlying object through specified serial executor.

    Attributes:
    - obj: underlying object.
    - executor: concurrent.futures.Executor - serial executor for session access.
    '''
    def __init__(self, obj, serial_executor: Executor):
        self.obj = obj
        self.executor = serial_executor

    def apply(self, fn):
        '''Apply fn to underlying object in self.executor'''
        callback = functools.partial(fn, self.obj)
        wrapped = self._teleport(self.executor, callback)
        return wrapped()

    @classmethod
    def _teleport(cls, executor, callback):
        '''Schedules callback in executor, returns a future-handle.
        Implemented in subclasses.
        '''
        raise NotImplementedError

class FutureSafeWrapper(BaseSafeWrapper):
    '''Provides concurrent.futures futures

    Example:
    >>> item = DbEntity(id=1)
    >>> add_future = safe_session.apply(lambda s: s.add(item))
    >>> # Block to ensure insert finished
    >>> add_future.result()
    '''
    @classmethod
    def _teleport(cls, executor, callback):
        def wrapped(*args, **kwargs):
            return executor.submit(callback, *args, **kwargs)

        return wrapped

class AwaitableSafeWrapper(BaseSafeWrapper):
    '''Provides asyncio awaitables

    Example:
    >>> item = DbEntity(id=1)
    >>> await async_safe_session.apply(lambda s: s.add(item))
    '''
    @classmethod
    def _teleport(cls, executor, callback):
        '''Throws RuntimeError if not in asyncio loop context.'''
        def wrapped(*args, **kwargs):
            return asyncio._get_running_loop().run_in_executor(
                executor, functools.partial(callback, *args, **kwargs)
            )

        return wrapped
