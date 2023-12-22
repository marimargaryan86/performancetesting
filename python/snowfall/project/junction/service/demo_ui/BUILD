python_sources(
    overrides={
        "main.py": {
            "dependencies": [
                "./static:static",
                "./templates:templates",
            ],
        },
    },
)
python_image(
    name="main",
    entry_point="main.py",
)
