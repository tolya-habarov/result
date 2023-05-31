from __future__ import annotations

from result import Err, Ok, Result


def test_pattern_matching_on_ok_type() -> None:
    """
    Pattern matching on ``Ok()`` matches the contained value.
    """
    o: Result[str, int] = Ok("yay")
    match o:
        case Ok(value):
            reached = True

    assert value == "yay"  # type:ignore
    assert reached  # type:ignore


def test_pattern_matching_on_err_type() -> None:
    """
    Pattern matching on ``Err()`` matches the contained value.
    """
    n: Result[int, str] = Err("nay")
    match n:
        case Err(value):
            reached = True

    assert value == "nay"  # type:ignore
    assert reached  # type:ignore
