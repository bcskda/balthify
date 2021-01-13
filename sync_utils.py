import asyncio
from concurrent.futures import Future, Executor
import functools
import typing
from sqlalchemy import Session

class BaseSafeSession:
    '''Interface. Accesses underlying session through specified serial executor.

    Attributes:
    - session: sqlalchemy.Session - underlying DB session.
    - executor: concurrent.futures.Executor - serial executor for session access.

    Note: only method calls allowed. Use `safe_session.executor` to access
        other attributes.
    '''
    def __init__(self, session: Session, serial_executor: Executor):
        self.session = session
        self.executor = serial_executor

    def __getattr__(self, name):
        # Pass possible AttributeError up
        # Assumes Session.__getattr__ is safe
        attr = getattr(self.session, name)
        print(self, name, attr)
        if not callable(attr):
            mesg = 'Attribute {} of type {} is not callable' \
                .format(name, type(attr))
            raise ValueError(mesg)
        return self._wrap(self.executor, attr)

    def __setattr__(self, name):
        raise ValueError('Setting (any) attributes not allowed')

    def apply(self, fn):
        '''Apply fn to self.session in self.executor'''
        callback = functools.partial(fn, session)
        wrapped = self._wrap(self.executor, callback)
        return wrapped()

    @classmethod
    def _wrap(cls, executor, callback):
        '''Get a safe-wrapped callback and update type hints'''
        cb_return = typing.get_type_hints(callback).get('return')
        wrapped = cls._teleport(executor, callback, cb_return)
        # Update return type hint if present in callback
        wraps_kwargs = dict(updated='return') if cb_return or dict()
        return functools.wraps(callback, **wraps_kwargs)(wrapped)

    @classmethod
    def _teleport(cls, executor, callback):
        '''Schedules callback in executor, returns a future-handle.

        Implemented in subclasses.
        Returned wrapper should specify new return value type hint.
        '''
        raise NotImplementedError

class FutureSafeSession(BaseSafeSession):
    '''Provides concurrent.futures futures

    Example:
    >>> item = DbEntity(id=1)
    >>> add_future = safe_session.add(item)
    >>> # Block to ensure insert finished
    >>> add_future.result()
    '''
    @classmethod
    def _teleport(cls, executor, callback, cb_return_hint):
        def wrapped(*args, **kwargs) -> typing.Future[cb_return_hint]:
            return executor.submit(callback, args=args, kwargs=kwargs)

        return wrapped

class AwaitableSafeSession(BaseSafeSession):
    '''Provides asyncio awaitables

    Example:
    >>> item = DbEntity(id=1)
    >>> await async_safe_session.add(item)
    '''
    @classmethod
    def _teleport(cls, executor, callback, cb_return_hint):
        '''Throws RuntimeError if not in asyncio loop context.'''
        def wrapped(*args, **kwargs) -> typing.Awaitable[cb_return_hint]:
            return asyncio.get_running_loop.run_in_executor(
                executor, functools.partial(callback, *args, **kwargs)
            )

        return wrapped
