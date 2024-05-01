python_sources(
    dependencies=["python/snowfall/project/fti/openapi"],
    overrides={
        "main.py": {
            "dependencies": ["vendor#asyncpg"],
        },
    },
)
python_image(
    name="main",
    entry_point="main.py",
)
python_tests(name="tests")
python_test_utils(name="test_utils")
