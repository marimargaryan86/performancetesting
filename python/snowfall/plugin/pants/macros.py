def python_image(  # type: ignore[no-untyped-def]
    namespace: str,
    name: str,
    debug: bool = False,
    **kwargs,
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

    # python:3.10.5-slim-bullseye
    tag_sha = "df9e675c0f6f0f758f7d49ea1b4e12cf7b8688d78df7d9986085fa0f24933ade"

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        instructions=[
            "ARG REGISTRY",
            "FROM ${{REGISTRY}}python@sha256:{hash} AS runtime".format(hash=tag_sha),
            'ENV PIP_NO_CACHE_DIR "false"',
            "ENV PYTHONASYNCIODEBUG {0}".format(1 if debug else 0),
            "ENV PYTHONFAULTHANDLER 1",
            'ENV PYTHONHASHSEED "random"',
            "ENV PYTHONUNBUFFERED 1",
            'ENV LOG_LEVEL "{0}"'.format("DEBUG" if debug else "INFO"),
            "COPY {namespace}/{name}.pex /bin/{name}".format(
                namespace=namespace,
                name=name,
            ),
            'ARG VERSION "dev"',
            "ENV VERSION $VERSION",
            'LABEL vendor="Snowfall Limited"',
            "LABEL com.snowfalltravel.version=$VERSION",
            "RUN /usr/local/bin/python3.10 /bin/{name} --help".format(name=name),
            'ENTRYPOINT ["/usr/local/bin/python3.10", "-Wdefault", "/bin/{0}"]'.format(
                name,
            ),
        ],
    )
