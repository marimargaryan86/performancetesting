def go_image(  # type: ignore[no-untyped-def]
    name: str,
    **kwargs,  # noqa: ANN003
) -> None:
    go_binary(  # type: ignore[name-defined]  # noqa: F821
        name=name,
        **(
            {
                "restartable": True,
            }
            | kwargs
        ),
    )

    # latest
    tag_sha = "ccaef5ee2f1850270d453fdf700a5392534f8d1a8ca2acda391fbb6a06b81c86"

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        instructions=[
            "FROM gcr.io/distroless/base@sha256:{hash} AS runtime".format(
                hash=tag_sha,
            ),
            "COPY {namespace}/{name} /bin/{name}".format(
                namespace=".".join(
                    build_file_dir().parts,  # type: ignore[name-defined]  # noqa: F821
                ),
                name=name,
            ),
            'ARG VERSION "dev"',
            "ENV VERSION $VERSION",
            'LABEL vendor="Snowfall Limited"',
            "LABEL com.snowfalltravel.version=$VERSION",
            'ENTRYPOINT ["/bin/{0}"]'.format(name),
        ],
    )


def python_image(  # type: ignore[no-untyped-def]
    name: str,
    **kwargs,  # noqa: ANN003
) -> None:
    pex_binary(  # type: ignore[name-defined]  # noqa: F821
        name=name,
        **(
            {
                "restartable": True,
            }
            | kwargs
            | {
                "execution_mode": "venv",
                "layout": "packed",
            }
        ),
    )

    # python:3.11.2-slim-bullseye
    tag_sha = "f776eb0acc768c0227cd336e33a97f3054101cf35ee6d5d8dc51b82349429925"

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        instructions=[
            "ARG REGISTRY",
            "FROM ${{REGISTRY}}python@sha256:{hash} AS runtime".format(hash=tag_sha),
            'ENV PIP_NO_CACHE_DIR "false"',
            "ENV PYTHONFAULTHANDLER 1",
            'ENV PYTHONHASHSEED "random"',
            "ENV PYTHONUNBUFFERED 1",
            "COPY {namespace}/{name}.pex /bin/{name}".format(
                namespace=".".join(
                    build_file_dir().parts,  # type: ignore[name-defined]  # noqa: F821
                ),
                name=name,
            ),
            'ARG VERSION "dev"',
            "ENV VERSION $VERSION",
            'LABEL vendor="Snowfall Limited"',
            "LABEL com.snowfalltravel.version=$VERSION",
            "RUN /usr/local/bin/python3.11 /bin/{name} --help".format(name=name),
            'ENTRYPOINT ["/usr/local/bin/python3.11", "-Wdefault", "/bin/{0}"]'.format(
                name,
            ),
        ],
    )
