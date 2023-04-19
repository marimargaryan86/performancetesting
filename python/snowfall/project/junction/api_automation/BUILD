python_test_utils(
    name="test_utils",
)

python_tests(
    sources=[
        "backend_api_tests/*",
        "mobile_api_tests/*",
        "planner_tests/*",
    ],
    name="tests",
    dependencies=[":resources"],
)

resources(name="resources", sources=["resources/*"])
