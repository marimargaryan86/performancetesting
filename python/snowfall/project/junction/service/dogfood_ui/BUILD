python_sources(
    overrides={
        "main.py": {
            "dependencies": ["./static", "./templates", "vendor#jinja2"],
        },
    },
)
python_image(
    name="main",
    entry_point="main.py",
)
