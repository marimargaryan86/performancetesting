python_sources(dependencies=["python/snowfall:airports"])
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=["python/snowfall:airports"])
files(
    name="fixtures",
    sources=["fixtures/**"],
)
python_image(
    name="main",
    entry_point="main.py",
)
