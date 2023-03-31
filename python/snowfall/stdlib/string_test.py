import pytest

from snowfall.stdlib import string


def test_random() -> None:
    random_string = string.random(32)
    assert len(random_string) == 32

    random_string = string.random(4, charset=["a"])
    assert random_string == "aaaa"


@pytest.mark.parametrize(
    ("snake_case", "expected"),
    [
        ("", ""),
        ("test", "test"),
        ("test_word", "testWord"),
        ("test_word_foobar", "testWordFoobar"),
        ("Test_word_foobar", "testWordFoobar"),
        ("test-word different_spacing", "testWordDifferentSpacing"),
        ("t", "t"),
    ],
)
def test_to_lower_camel(
    snake_case: str,
    expected: str,
) -> None:
    assert string.to_lower_camel(snake_case) == expected


@pytest.mark.parametrize(
    ("snake_case", "expected"),
    [
        ("", ""),
        ("test", "Test"),
        ("test_word", "TestWord"),
        ("test_word_foobar", "TestWordFoobar"),
        ("Test_word_foobar", "TestWordFoobar"),
        ("test-word different_spacing", "TestWordDifferentSpacing"),
        ("t", "T"),
    ],
)
def test_to_upper_camel(
    snake_case: str,
    expected: str,
) -> None:
    assert string.to_upper_camel(snake_case) == expected


@pytest.mark.parametrize(
    ("camel_case", "expected"),
    [
        ("", ""),
        ("test", "test"),
        ("testWord", "test_word"),
        ("testWordFoobar", "test_word_foobar"),
        ("test_test", "test_test"),
        ("TestTest", "test_test"),
        ("TestTestTest", "test_test_test"),
    ],
)
def test_to_snake(
    camel_case: str,
    expected: str,
) -> None:
    assert string.to_snake(camel_case) == expected
