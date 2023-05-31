from __future__ import annotations

import functools
import inspect
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

if sys.version_info >= (3, 10):
    from typing import Final, ParamSpec, TypeAlias
else:
    from typing_extensions import Final, ParamSpec, TypeAlias


T = TypeVar('T', covariant=True)  # Success type
E = TypeVar('E', covariant=True)  # Error type
U = TypeVar('U')
P = ParamSpec('P')
R = TypeVar('R')
TBE = TypeVar('TBE', bound=BaseException)


class Ok(Generic[T]):
    """
    A value that indicates success and which stores arbitrary data for the return value.
    """

    _value: T
    __match_args__ = ('value',)
    __slots__ = ('_value',)

    @overload
    def __init__(self) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(self, value: T) -> None:
        ...  # pragma: no cover

    def __init__(self, value: Any = True) -> None:
        self._value = value

    def __repr__(self) -> str:
        return 'Ok({})'.format(repr(self._value))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ok) and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((True, self._value))

    def unwrap(self) -> T:
        """
        Return the value.
        """
        return self._value

    def unwrap_or(self, _default: U) -> T:
        """
        Return the value.
        """
        return self._value

    def err(self) -> E:
        """
        Raises an `UnwrapError`.
        """
        raise UnwrapError(self, 'Called `Result.err()` on an `Ok` value')


class Err(Generic[E]):
    """
    A value that signifies failure and which stores arbitrary data for the error.
    """

    __match_args__ = ('value',)
    __slots__ = ('_value',)

    def __init__(self, value: E) -> None:
        self._value = value

    def __repr__(self) -> str:
        return 'Err({})'.format(repr(self._value))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Err) and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((False, self._value))

    def unwrap(self) -> NoReturn:
        """
        Raises an `UnwrapError`.
        """
        raise UnwrapError(self, 'Called `Result.unwrap()` on an `Err` value')

    def unwrap_or(self, default: U) -> U:
        """
        Return `default`.
        """
        return default

    def err(self) -> E:
        """
        Return the error.
        """
        return self._value


# define Result as a generic type alias for use
# in type annotations
"""
A simple `Result` type inspired by Rust.
Not all methods (https://doc.rust-lang.org/std/result/enum.Result.html)
have been implemented, only the ones that make sense in the Python context.
"""
Result: TypeAlias = Union[Ok[T], Err[E]]

"""
A type to use in `isinstance` checks.
This is purely for convenience sake, as you could also just write `isinstance(res, (Ok, Err))
"""
OkErr: Final = (Ok, Err)


class UnwrapError(Exception):
    """
    Exception raised from ``.unwrap_<...>`` and ``.expect_<...>`` calls.

    The original ``Result`` can be accessed via the ``.result`` attribute, but
    this is not intended for regular use, as type information is lost:
    ``UnwrapError`` doesn't know about both ``T`` and ``E``, since it's raised
    from ``Ok()`` or ``Err()`` which only knows about either ``T`` or ``E``,
    not both.
    """

    _result: Result[object, object]

    def __init__(self, result: Result[object, object], message: str) -> None:
        self._result = result
        super().__init__(message)

    @property
    def result(self) -> Result[Any, Any]:
        """
        Returns the original result.
        """
        return self._result


def as_result(
    exceptions: Optional[Tuple[Type[TBE], ...]] = None,
) -> Callable[[Callable[P, R]], Callable[P, Result[R, TBE]]]:
    """
    Make a decorator to turn a function into one that returns a ``Result``.

    Regular return values are turned into ``Ok(return_value)``. Raised
    exceptions of the specified exception type(s) are turned into ``Err(exc)``.
    """

    if exceptions is None:
        exceptions = (Exception,)  # type:ignore

    if not exceptions or not all(
        inspect.isclass(exception) and issubclass(exception, BaseException)
        for exception in exceptions
    ):
        raise TypeError('as_result() requires one or more exception types')

    def decorator(f: Callable[P, R]) -> Callable[P, Result[R, TBE]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                return Ok(f(*args, **kwargs))
            except exceptions as exc:  # type:ignore
                return Err(exc)

        return wrapper

    return decorator


def as_async_result(
    exceptions: Optional[Tuple[Type[TBE], ...]] = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[Result[R, TBE]]]]:
    """
    Make a decorator to turn an async function into one that returns a ``Result``.
    Regular return values are turned into ``Ok(return_value)``. Raised
    exceptions of the specified exception type(s) are turned into ``Err(exc)``.
    """

    if exceptions is None:
        exceptions = (Exception,)  # type:ignore

    if not exceptions or not all(
        inspect.isclass(exception) and issubclass(exception, BaseException)
        for exception in exceptions
    ):
        raise TypeError('as_result() requires one or more exception types')

    def decorator(
        f: Callable[P, Awaitable[R]]
    ) -> Callable[P, Awaitable[Result[R, TBE]]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        @functools.wraps(f)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                return Ok(await f(*args, **kwargs))
            except exceptions as exc:  # type:ignore
                return Err(exc)

        return async_wrapper

    return decorator
