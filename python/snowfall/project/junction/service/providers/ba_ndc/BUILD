python_sources(dependencies=["python/snowfall:airports"])
python_test_utils(
    name="test_utils", dependencies=["python/snowfall:airports", ":fixtures"]
)
python_image(
    name="main",
    entry_point="main.py",
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_tests(name="tests")
