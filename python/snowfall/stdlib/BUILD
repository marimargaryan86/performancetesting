python_sources()
python_tests(name="tests")

__dependencies_rules__(
    (
        "*",
        (
            "protobuf/snowfall/stdlib/**",
            "python/snowfall/conftest.py",
            "python/snowfall/fixtures.py",
            "python/snowfall/stdlib/**",
            "vendor#*",
        ),
        "!*",
    )
)

__defaults__(
    {
        (python_test, python_tests): dict(
            batch_compatibility_tag="stdlib",
        ),
    },
    extend=True,
)
