python_image(
    name="main",
    entry_point="main.py",
)

python_sources(
    dependencies=["openapi/junction/pay_api", "openapi/junction/pay_admin_api"]
)

python_test_utils(
    name="test_utils",
    dependencies=["openapi/junction/pay_api", "openapi/junction/pay_admin_api"],
)
python_tests(name="tests")
