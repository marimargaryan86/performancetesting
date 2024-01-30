python_sources(dependencies=["python/snowfall/data:airports"])
python_tests(
    name="tests", dependencies=["python/snowfall/vendor/ask2go:fixtures", ":fixtures"]
)
files(
    name="fixtures",
    sources=["fixtures/**"],
)
python_image(
    name="main",
    entry_point="main.py",
)
