python_sources(name="src", sources=["**/*.py"])

python_image(
    name="main",
    script="pytest",
    args=[
        "--asyncio-mode=auto",
    ],
    dependencies=["vendor#pytest-asyncio", "vendor#allure-pytest", ":src"],
    is_service=False,
)
