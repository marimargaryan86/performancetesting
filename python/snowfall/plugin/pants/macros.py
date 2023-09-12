def nomad_template(  # noqa: WPS210
    commands: list[str],  # noqa: SF20
    service_entry_point: str = "",
    name: str = "",
) -> None:
    if not name:
        name = build_file_dir().name  # type: ignore[name-defined]  # noqa: F821

    cmd = './bash/lint-configuration.sh {command} "{path}/{filename}.nomad" "{config}"'
    config_path = "{path}/debug_info.json".format(
        path=build_file_dir(),  # type: ignore[name-defined]  # noqa: F821
    )

    if service_entry_point:
        adhoc_tool(  # type: ignore[name-defined]  # noqa: F821
            name="{name}_debug_info".format(name=name),
            runnable=service_entry_point,
            args=["--debug-info"],
            stdout=config_path,
            output_files=[config_path],
            workdir="/",
        )

    for command_def in commands:
        parts = command_def.split("#")

        if len(parts) == 1:
            command, filename = parts[0], parts[0]
        else:
            command, filename = parts[1], parts[0]

        file(  # type: ignore[name-defined]  # noqa: F821
            name="{name}_{filename}_config".format(name=name, filename=filename),
            source="{filename}.json".format(filename=filename),
        )

        file(  # type: ignore[name-defined]  # noqa: F821
            name="{name}_{filename}_nomad".format(name=name, filename=filename),
            source="{filename}.nomad".format(filename=filename),
        )

        if service_entry_point:
            experimental_test_shell_command(  # type: ignore[name-defined]  # noqa: F821
                name="{name}_{filename}_test".format(name=name, filename=filename),
                command=cmd.format(
                    command=command,
                    filename=filename,
                    path=build_file_dir(),  # type: ignore[name-defined]  # noqa: F821
                    config=config_path,
                ),
                execution_dependencies=[
                    ":{name}_{filename}_config".format(name=name, filename=filename),
                    ":{name}_{filename}_nomad".format(name=name, filename=filename),
                    ":{name}_debug_info".format(name=name),
                    "bash/lint-configuration.sh",
                ],
                tools=["bash", "jq", "perl"],
                workdir="/",
            )


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
    tag_sha = "46c5b9bd3e3efff512e28350766b54355fce6337a0b44ba3f822ab918eca4520"

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        instructions=[
            "FROM gcr.io/distroless/base-debian11@sha256:{hash} AS runtime".format(
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
    **kwargs,  # noqa: ANN003
) -> None:
    try:
        name = kwargs["name"]
    except KeyError:
        name = build_file_dir().name  # type: ignore[name-defined]  # noqa: F821

    offenders = {
        "python/snowfall/project/junction/go/service/places/places.py": {
            "python/snowfall/project/junction/extensions/service/mobile_api/places_migration.py",
        },
    }

    __dependents_rules__(  # type: ignore[name-defined]  # noqa: F821
        *(
            (
                {"path": "//{0}".format(offended_file)},
                "/**",
                *(
                    "?//{0}".format(offending_file)
                    for offending_file in offending_files
                ),
                "!*",
            )
            for offended_file, offending_files in offenders.items()
        ),
        (
            {"path": "/**"},
            "/**",
            "!*",
        ),
        ("*", "!*"),
    )

    __defaults__(  # type: ignore[name-defined]  # noqa: F821
        {
            (python_test, python_tests): {  # type: ignore[name-defined]  # noqa: F821
                "batch_compatibility_tag": str(build_file_dir()),  # type: ignore[name-defined]  # noqa: F821
            },
        },
        extend=True,
    )

    pex_binary(  # type: ignore[name-defined]  # noqa: F821
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

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        instructions=[
            "FROM cgr.dev/chainguard/wolfi-base:latest@sha256:{hash} AS runtime".format(
                hash="f73a3360466ecc4d6df3f451d7d5c4c49663096e158848ddbc9603c52a47bffe",
            ),
            (
                "RUN apk update && apk add --no-cache --update-cache"
                " python-3.11~=3.11.5 tzdata~=2023c"
            ),
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
            'ENTRYPOINT ["python", "-Wdefault", "-Xfaulthandler", "/bin/{0}"]'.format(
                name,
            ),
        ],
    )
