python_image(
    name="main",
    entry_point="main.py",
)

python_sources()


python_test_utils(
    name="test_utils",
)

python_tests(
    name="tests",
    dependencies=[":fixtures"],
)

files(
    name="fixtures",
    sources=["fixtures/*"],
)
