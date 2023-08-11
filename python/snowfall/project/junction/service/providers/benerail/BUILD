python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":benerail_stations"])

resource(
    name="benerail_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-fb50d62317c071b594dc1d32ce61f79cd1846dabaccf0b59f32d7b94c5ef2a3a.json",
        len=3898566,
        sha256="fb50d62317c071b594dc1d32ce61f79cd1846dabaccf0b59f32d7b94c5ef2a3a",
        filename="benerail_stations.json",
    ),
)
