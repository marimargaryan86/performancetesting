python_sources(dependencies=[":borders"])
python_image(
    name="main",
    entry_point="main.py",
)

resource(
    name="borders",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/EEZ_land_union_v3_202003-198dfb029c8b98840e5d9e164ed7cb5fc089ec644c54efe47fbd1009578f686f.zip",
        len=19932478,
        sha256="198dfb029c8b98840e5d9e164ed7cb5fc089ec644c54efe47fbd1009578f686f",
        filename="EEZ_land_union_v3_202003.zip",
    ),
)
