import pytest

from snowfall.stdlib import string


def test_random() -> None:
    random_string = string.random(32)
    assert len(random_string) == 32

    random_string = string.random(4, charset=["a"])
    assert random_string == "aaaa"


@pytest.mark.parametrize(
    "snake_case,expected",
    [
        ("", ""),
        ("test", "test"),
        ("test_word", "testWord"),
        ("test_word_foobar", "testWordFoobar"),
    ],
)
def test_to_camel(
    snake_case: str,
    expected: str,
) -> None:
    assert string.to_camel(snake_case) == expected


@pytest.mark.parametrize(
    "camel_case,expected",
    [
        ("", ""),
        ("test", "test"),
        ("testWord", "test_word"),
        ("testWordFoobar", "test_word_foobar"),
    ],
)
def test_to_snake(
    camel_case: str,
    expected: str,
) -> None:
    assert string.to_snake(camel_case) == expected
