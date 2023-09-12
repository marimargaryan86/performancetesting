python_sources(dependencies=["python/snowfall/data:airports"])
python_test_utils(
    name="test_utils", dependencies=["python/snowfall/data:airports", ":fixtures"]
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
