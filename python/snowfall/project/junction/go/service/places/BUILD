python_sources(dependencies=[":cities", ":nodes"])
python_image(
    name="main",
    entry_point="main.py",
)
resource(
    name="cities",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/places_ascii-abe836e885fba3e3d63c4f17b145245756649ba040e4b89d163d962b6d9e6426.csv",
        len=8082465,
        sha256="abe836e885fba3e3d63c4f17b145245756649ba040e4b89d163d962b6d9e6426",
        filename="cities.csv",
    ),
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
