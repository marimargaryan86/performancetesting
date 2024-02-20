python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":routes", ":ports"])
python_test_utils(name="test_utils")
python_tests(name="tests", dependencies=[":fixtures", ":ports", ":routes"])

files(
    name="fixtures",
    sources=["fixtures/**"],
)
resource(
    name="routes",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/df-routes-e19416278999f2f0cdf7d063bb8287fe747dd2ffcea22aaa70e003210e2f8d54.json",
        len=1418865,
        sha256="e19416278999f2f0cdf7d063bb8287fe747dd2ffcea22aaa70e003210e2f8d54",
        filename="routes.json",
    ),
)
resource(
    name="ports",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/df-ports-864b8ea4b32d91b1009a3e1ed7a1789ce31b13e643ce94d2fa3a7e3576c406f9.json",
        len=95798,
        sha256="864b8ea4b32d91b1009a3e1ed7a1789ce31b13e643ce94d2fa3a7e3576c406f9",
        filename="ports.json",
    ),
)
