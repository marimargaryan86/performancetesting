import itertools
import sys
from os import path
from typing import Mapping, Sequence

import hcl2
import pydantic


class _Configuration(pydantic.BaseModel):
    class _Environment(pydantic.BaseModel):  # noqa: WPS431
        deploy: bool = True
        variables: Mapping[str, str | bool | int | float] = {}

    development: _Environment
    production: _Environment


_Mapping = Sequence[Mapping[str, Mapping[str, "_Mapping"]]]


def _validate_jobs(  # noqa: WPS210
    template_path: str,
    filename: str,
    jobs: _Mapping,
) -> bool:
    errors = False
    expected_job_name = "{0}-{1}".format(
        path.basename(path.dirname(template_path)),
        filename,
    )

    for job in jobs:
        for job_name, job_data in job.items():
            if job_name != expected_job_name:
                errors = True
                _log_error(
                    '{0}: job "{1}" should be "{2}"'.format(
                        template_path,
                        job_name,
                        expected_job_name,
                    ),
                )

            has_errors = _validate_groups(
                template_path,
                filename,
                job_name,
                job_data.get("group", []),
            )

            if has_errors:
                errors = True

    return errors


def _validate_groups(
    template_path: str,
    filename: str,
    job_name: str,
    groups: _Mapping,
) -> bool:
    errors = False

    for group in groups:
        for group_name, group_data in group.items():
            if group_name != filename:
                errors = True
                _log_error(
                    '{0}: group "{1}" in job "{2}" should be "{3}"'.format(
                        template_path,
                        group_name,
                        job_name,
                        filename,
                    ),
                )

            # todo: validate services?
            has_errors = _validate_tasks(
                template_path,
                filename,
                job_name,
                group_name,
                group_data.get("task", []),
            )

            if has_errors:
                errors = True

    return errors


def _validate_tasks(
    template_path: str,
    filename: str,
    job_name: str,
    group_name: str,
    tasks: _Mapping,
) -> bool:
    errors = False

    for task in tasks:
        for task_name, task_data in task.items():
            if "lifecycle" not in task_data and task_name != filename:
                errors = True
                _log_error(
                    (
                        '{0}: task "{1}" in group "{2}" in job "{3}"'
                        + ' should be "{4}"'
                    ).format(
                        template_path,
                        task_name,
                        group_name,
                        job_name,
                        filename,
                    ),
                )

    return errors


def _expected_variables(variables: _Mapping) -> frozenset[str]:
    return frozenset(
        (
            variable_name
            for variable_name in itertools.chain(
                *[nomad_var.keys() for nomad_var in variables],
            )
            if variable_name
            not in {
                "datacenter",
                "docker_image",
                "environment",
                "registry_address",
                "registry_password",
                "registry_username",
            }
        ),
    )


def _load_config_file(
    template_path: str,
) -> _Configuration | None:
    config_path = "{0}.json".format(path.splitext(template_path)[0])

    try:
        return _Configuration.parse_file(config_path)
    except FileNotFoundError:
        return None
    except pydantic.ValidationError as err:
        _log_error(
            "{0}: {1}".format(
                config_path,
                str(err),
            ),
        )
        return None


def _validate_variables(
    template_path: str,
    variables: _Mapping,
) -> bool:
    config_data = _load_config_file(template_path)

    if not config_data:
        return False

    errors = False

    for environment, env_data in config_data:
        if not env_data.deploy:
            continue

        for nomad_var in _expected_variables(variables):
            if nomad_var not in env_data.variables.keys():
                errors = True
                _log_error(
                    '{0}: variable "{1}" is not configured in environment "{2}"'.format(
                        template_path,
                        nomad_var,
                        environment,
                    ),
                )

    return errors


def _log_error(msg: str) -> None:
    print(msg, file=sys.stderr)  # noqa: WPS421


def _main() -> bool:
    if len(sys.argv) < 2:
        _log_error(
            "usage: {0} path/to/job.nomad path/to/job2.nomad".format(sys.argv[0]),
        )
        sys.exit(1)

    errors = False

    for template_path in sys.argv[1:]:
        filename = path.splitext(
            path.basename(template_path),
        )[
            0
        ].replace("_", "-")

        with open(template_path, "r") as template_file:
            parsed = hcl2.load(template_file)

            if _validate_jobs(template_path, filename, parsed.get("job", [])):
                errors = True

            if _validate_variables(template_path, parsed.get("variable", [])):
                errors = True

    return errors


if _main():
    sys.exit(1)
