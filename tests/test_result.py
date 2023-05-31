from __future__ import annotations

from typing import Callable

import pytest

from result import Err, Ok, OkErr, Result, UnwrapError, as_async_result, as_result


def test_eq() -> None:
    assert Ok(1) == Ok(1)
    assert Err(1) == Err(1)
    assert Ok(1) != Err(1)
    assert Ok(1) != Ok(2)
    assert Err(1) != Err(2)
    assert not (Ok(1) != Ok(1))
    assert Ok(1) != "abc"
    assert Ok("0") != Ok(0)


def test_hash() -> None:
    assert len({Ok(1), Err("2"), Ok(1), Err("2")}) == 2
    assert len({Ok(1), Ok(2)}) == 2
    assert len({Ok("a"), Err("a")}) == 2


def test_repr() -> None:
    """
    ``repr()`` returns valid code if the wrapped value's ``repr()`` does as well.
    """
    o = Ok(123)
    n = Err(-1)

    assert repr(o) == "Ok(123)"
    assert o == eval(repr(o))

    assert repr(n) == "Err(-1)"
    assert n == eval(repr(n))


def test_unwrap() -> None:
    o = Ok('yay')
    n = Err('nay')
    assert o.unwrap() == 'yay'
    with pytest.raises(UnwrapError):
        n.unwrap()


def test_unwrap_or() -> None:
    o = Ok('yay')
    n = Err('nay')
    assert o.unwrap_or('some_default') == 'yay'
    assert n.unwrap_or('another_default') == 'another_default'


def test_isinstance_result_type() -> None:
    o = Ok('yay')
    n = Err('nay')
    assert isinstance(o, OkErr)
    assert isinstance(n, OkErr)
    assert not isinstance(1, OkErr)


def test_error_context() -> None:
    n = Err('nay')
    with pytest.raises(UnwrapError) as exc_info:
        n.unwrap()
    exc = exc_info.value
    assert exc.result is n


def test_slots() -> None:
    """
    Ok and Err have slots, so assigning arbitrary attributes fails.
    """
    o = Ok('yay')
    n = Err('nay')
    with pytest.raises(AttributeError):
        o.some_arbitrary_attribute = 1  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        n.some_arbitrary_attribute = 1  # type: ignore[attr-defined]


def test_as_result() -> None:
    """
    ``as_result()`` turns functions into ones that return a ``Result``.
    """

    @as_result(exceptions=(ValueError,))
    def good(value: int) -> int:
        return value

    @as_result(exceptions=(IndexError, ValueError))
    def bad(value: int) -> int:
        raise ValueError

    good_result = good(123)
    bad_result = bad(123)

    assert isinstance(good_result, Ok)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Err)
    assert isinstance(bad_result.err(), ValueError)


def test_as_result_other_exception() -> None:
    """
    ``as_result()`` only catches the specified exceptions.
    """

    @as_result(exceptions=(ValueError,))
    def f() -> int:
        raise IndexError

    with pytest.raises(IndexError):
        f()


def test_as_result_type_checking() -> None:
    """
    The ``as_result()`` is a signature-preserving decorator.
    """

    @as_result(exceptions=(ValueError,))
    def f(a: int) -> int:
        return a

    res: Result[int, ValueError]
    res = f(123)  # No mypy error here.
    assert res.unwrap() == 123


@pytest.mark.asyncio
async def test_as_async_result() -> None:
    """
    ``as_async_result()`` turns functions into ones that return a ``Result``.
    """

    @as_async_result(exceptions=(ValueError,))
    async def good(value: int) -> int:
        return value

    @as_async_result(exceptions=(IndexError, ValueError))
    async def bad(value: int) -> int:
        raise ValueError

    good_result = await good(123)
    bad_result = await bad(123)

    assert isinstance(good_result, Ok)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Err)
    assert isinstance(bad_result.err(), ValueError)


def sq(i: int) -> Result[int, int]:
    return Ok(i * i)


def to_err(i: int) -> Result[int, int]:
    return Err(i)


# Lambda versions of the same functions, just for test/type coverage
sq_lambda: Callable[[int], Result[int, int]] = lambda i: Ok(i * i)
to_err_lambda: Callable[[int], Result[int, int]] = lambda i: Err(i)
