python_sources(dependencies=["python/snowfall/data:airports"])
python_tests(
    name="tests", dependencies=["python/snowfall/vendor/duffel:fixtures", ":fixtures"]
)
files(
    name="fixtures",
    sources=["fixtures/**"],
)
