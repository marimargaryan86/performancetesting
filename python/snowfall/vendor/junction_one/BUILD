python_sources()

python_test_utils(
    name="test_utils",
    dependencies=[":fixtures"],
)

python_tests(name="tests")

shell_sources(name="regenerate_script")

files(
    name="fixtures",
    sources=["fixtures/*"],
)
