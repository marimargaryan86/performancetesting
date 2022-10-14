python_sources(
    overrides={
        "routes.py": {
            "dependencies": [":layout"],
        },
    },
)
pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
)
resource(
    name="layout",
    source="layout.html",
)
