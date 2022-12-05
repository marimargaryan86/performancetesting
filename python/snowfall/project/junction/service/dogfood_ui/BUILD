python_sources(
    overrides={
        "main.py": {
            "dependencies": ["./static", "./templates", "vendor#jinja2"],
        },
    },
)
python_image(
    namespace="python.snowfall.project.junction.service.dogfood_ui",
    name="main",
    entry_point="main.py",
)
