python_sources()
python_tests(
    name="tests", dependencies=["python/snowfall/vendor/duffel:fixtures", ":fixtures"]
)
files(
    name="fixtures",
    sources=["fixtures/**"],
)
python_image(
    name="main",
    entry_point="main.py",
)
