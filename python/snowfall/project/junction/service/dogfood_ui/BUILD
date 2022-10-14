python_sources(
    overrides={
        "routes.py": {
            "dependencies": [":layout"],
        },
    },
)
python_image(
    namespace="python.snowfall.project.junction.service.dogfood_ui",
    name="main",
    entry_point="main.py",
)
resource(
    name="layout",
    source="layout.html",
)
