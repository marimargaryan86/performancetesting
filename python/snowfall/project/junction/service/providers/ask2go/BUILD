python_sources(dependencies=[":airports"])
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":airports"])
resources(
    name="airports",
    sources=["airport_coordinates.json"],
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
    execution_mode="venv",
)
docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
