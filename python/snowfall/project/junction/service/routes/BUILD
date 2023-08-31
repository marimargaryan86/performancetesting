python_sources(dependencies=[":nodes"])
python_image(
    name="main",
    entry_point="main.py",
)

resource(
    name="nodes",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/places_nodes-dcc421f8da7c34e8d00ff1f835c4bf81c5a225ead3c562434981203c5dd06d68.json",
        len=101574333,
        sha256="dcc421f8da7c34e8d00ff1f835c4bf81c5a225ead3c562434981203c5dd06d68",
        filename="nodes.json",
    ),
)
