# Testing

Writing tests is one of the fastest, most reliable and most reproducible
ways for a developer to get feedback about a code change they are currently
doing, and adds a safeguard that later code changes does not break expected
behaviour.

However, it is not always straight-forward to write a good test. Let's have
a look at a few different examples, trying to illustrate some best practices.

## What is a "test"?

It might sound like a silly question, but having seen how a lot of people
write tests, different people have different definitions. A better word than
simply "test" is probably "test case". Each test method should assert one
test case.

Take start with this example:

```py
def test_normalize_text() -> None:
    assert normalize_text("expe!cted") == "expected"
```

Just looking at the name of the test function first, this is a very common
naming pattern, it is also very bad. It's pretty obvious that a test for the
function `normalize_text` tests that function, so the naming is extremely
vague about what the test actually does.

If we look at the test code itself, we can see that the test checks if
the return value is `"expected"` for the input value`"expe!cted"`. If we now
also want to have a test case for some other input value, where would we
logically add that? Because of the bad test function naming, most people would
probably just extend it, like so:

```py
def test_normalize_text() -> None:
    assert normalize_text("expe!cted") == "expected"
    assert normalize_text("@expected") == "expected"
```

If we think about what the test case actually is, we are testing that
`normalize_text` removes special characters from the text. Let's rename the
test to something that reflects that.

```py
def test_normalize_text_removes_special_characters() -> None:
    ...
```

We should be able to read the test name as "Test (that) normalize_text
removes special characters". It's a little bit more clear what our test case
is now, but it's not perfect. If the case for `@` works, but `!` does not,
the test will simply fail, not giving us information that only one of the
test cases is failing. Say we also want to test a bunch of different special
characters, because someone opened a bug saying that `†` was not removed.

Let's parametrize the test, so we only assert one test case at a time:

```py
@pytest.mark.parametrize(
  ("input_value", "expected"),
  [
    ("expe!cted", "expected"),
    ("@expected", "expected"),
    ("expected†", "expected"),
  ],
)
def test_normalize_text_removes_special_characters(
    input_value: str,
    expected: str,
) -> None:
    assert normalize_text(input_value) == expected
```

With this we will test every test case by itself, and we can expand the list
whenever we get new test cases we want to make sure works.

Now, there is a separate test case we want to make sure is handled as well,
that certain characters are _not_ removed, because we want to keep
underscore (`_`) _in certain positions_, for example. Instead of expanding our
list of parametrized test cases, it's probably better to create a separate
test that just checks this:

```py
@pytest.mark.parametrize(
  ("input_value", "expected"),
  [
    ("expected_value", "expected_value"),
    ("_expected_value_", "expected_value"),
  ],
)
def test_normalize_text_keeps_certain_special_characters(
    input_value: str,
    expected: str,
) -> None:
    assert normalize_text(input_value) == expected
```

At some point, when we keep adding additional tests for other functions, it
might be appropriate to group our tests under one test class, making it
easier to find those specific tests while navigating a bigger test file:

```py
class TestNormalizeText(object):
    @pytest.mark.parametrize(...)
    def test_normalize_text_removes_special_characters(...) -> None:
        ...

    @pytest.mark.parametrize(...)
    def test_normalize_text_keeps_certain_special_characters(...) -> None:
        ...
```

### Summary

Assert only one test case per test, and name the test after which test case
we are asserting. Just looking at the names of the tests should give us an
overview of which functionality is covered by tests, but also what
functionality is expected by the code we are testing. As a rule of thumb, if
we can't come up with a good name for our test, we are probably either
testing too much functionality at once or we are not sure what functionality
we are actually testing.
