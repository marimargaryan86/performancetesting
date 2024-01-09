_BASE_IMAGE_SHA = "5bab300be31cd472c6f45ba7c059415b0bdeb0a49b32ecc12060394d642fd192"


def _generate_repository(build_file_dir, exclude: set[str]) -> str:  # type: ignore[no-untyped-def]  # noqa: ANN001
    repository = "{base_url}/{namespace}/{name}".format(
        base_url=env("CI_PROJECT_PATH", "").strip("/"),  # type: ignore[name-defined]  # noqa: F821
        namespace="-".join(
            [
                part.replace("_", "-")
                for part in build_file_dir.parent.parts
                if part not in exclude
            ],
        ).strip("/"),
        name=build_file_dir.name.replace("_", "-").strip("/"),
    )

    return repository.replace("//", "/").strip("/")


def _generate_service_name(repository: str) -> str:
    service_name = repository
    prefix = env("CI_PROJECT_PATH", "")  # type: ignore[name-defined]  # noqa: F821

    if prefix:
        service_name = service_name.removeprefix(prefix)

    return service_name.strip("/").replace("/", "-")


def nomad_template(
    commands: list[str],  # noqa: SF20
    service_entry_point: str = "",
    name: str = "",
) -> None:
    if not name:
        name = build_file_dir().name  # type: ignore[name-defined]  # noqa: F821

    cmd = './bash/lint-configuration.sh {command} "{path}/{filename}.nomad" "{config}" "{entry_point}"'
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
                    entry_point=service_entry_point,
                ),
                execution_dependencies=[
                    ":{name}_{filename}_config".format(name=name, filename=filename),
                    ":{name}_{filename}_nomad".format(name=name, filename=filename),
                    ":{name}_debug_info".format(name=name),
                    "bash/lint-configuration.sh",
                ],
                tools=["basename", "bash", "dirname", "jq", "perl"],
                workdir="/",
            )


def custom_image(prefix=None, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001,ANN003
    repository = "{base_url}/{prefix}/{namespace}/{name}".format(
        base_url=env("CI_PROJECT_PATH", ""),  # type: ignore[name-defined]  # noqa: F821
        prefix=prefix or "",
        namespace="-".join(
            [
                part.replace("_", "-")
                for part in build_file_dir().parent.parts[1:]  # type: ignore[name-defined]  # noqa: F821
            ],
        ),
        name=build_file_dir().name.replace("_", "-"),  # type: ignore[name-defined]  # noqa: F821
    )

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        **{
            **kwargs,
            "image_tags": ["{build_args.VERSION}"],
            "repository": repository.replace("//", "/").strip("/"),
        },
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

    repository = _generate_repository(
        build_file_dir(),  # type: ignore[name-defined]  # noqa: F821
        {"golang", "cmd"},
    )
    service_name = _generate_service_name(repository)

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        repository=repository,
        instructions=[
            "FROM cgr.dev/chainguard/wolfi-base:latest@sha256:{hash} AS runtime".format(
                hash=_BASE_IMAGE_SHA,
            ),
            (
                "RUN apk update && apk add --no-cache --update-cache"
                " glibc~=2.38 tzdata~=2023c"
            ),
            "COPY {namespace}/{name} /bin/{name}".format(
                namespace=".".join(
                    build_file_dir().parts,  # type: ignore[name-defined]  # noqa: F821
                ),
                name=name,
            ),
            'ARG VERSION "dev"',
            "ENV VERSION $VERSION",
            'ENV SENTRY_RELEASE "{service_name}@$VERSION"'.format(
                service_name=service_name.replace("/", "-"),
            ),
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

    repository = _generate_repository(
        build_file_dir(),  # type: ignore[name-defined]  # noqa: F821
        {"python", "snowfall", "project", "service"},
    )
    service_name = _generate_service_name(repository)

    docker_image(  # type: ignore[name-defined]  # noqa: F821
        name="{name}_docker".format(name=name),
        dependencies=[":{name}".format(name=name)],
        image_tags=["{build_args.VERSION}"],
        repository=repository,
        instructions=[
            "FROM cgr.dev/chainguard/wolfi-base:latest@sha256:{hash} AS runtime".format(
                hash=_BASE_IMAGE_SHA,
            ),
            (
                "RUN apk update && apk add --no-cache --update-cache"
                " python-3.11~=3.11.6 tzdata~=2023c"
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
            'ENV SENTRY_RELEASE "{service_name}@$VERSION"'.format(
                service_name=service_name.replace("/", "-"),
            ),
            'LABEL vendor="Snowfall Limited"',
            "LABEL com.snowfalltravel.version=$VERSION",
            'ENTRYPOINT ["python", "-Wdefault", "-Xfaulthandler", "/bin/{0}"]'.format(
                name,
            ),
        ],
    )
