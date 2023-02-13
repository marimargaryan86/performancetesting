python_image(
    namespace="python.snowfall.project.pay.service.pay_api",
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=["openapi/junction/pay_api"])

python_test_utils(
    name="test_utils",
    dependencies=["openapi/junction/pay_api"],
)
python_tests(name="tests")
