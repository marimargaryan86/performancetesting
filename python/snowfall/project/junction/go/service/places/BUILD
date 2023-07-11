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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/places_nodes-79d79366c231e8ad9b8e3ce31859a51ec0b4c846844a63f804e10fd5c8509d80.json",
        len=96083693,
        sha256="79d79366c231e8ad9b8e3ce31859a51ec0b4c846844a63f804e10fd5c8509d80",
        filename="nodes.json",
    ),
)
