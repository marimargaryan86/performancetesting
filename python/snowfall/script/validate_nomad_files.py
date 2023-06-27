import itertools
import sys
from collections.abc import Mapping, Sequence
from os import path

import pydantic

from snowfall.stdlib.format import hcl2


class _Configuration(pydantic.BaseModel):
    class _Environment(pydantic.BaseModel):  # noqa: WPS431
        deploy: bool = True
        variables: Mapping[
            str,
            str | bool | int | float | list[str | bool | int | float],
        ] = {}

    development: _Environment
    production: _Environment
    sandbox: _Environment


def _validate_jobs(  # noqa: WPS210
    template_path: str,
    filename: str,
    jobs: Sequence[Mapping[str, hcl2.Job]],
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
                job_data.group,
            )

            if has_errors:
                errors = True

    return errors


def _validate_groups(
    template_path: str,
    filename: str,
    job_name: str,
    groups: Sequence[Mapping[str, hcl2.Group]],
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

            # TODO: validate services?
            has_errors = _validate_tasks(
                template_path,
                filename,
                job_name,
                group_name,
                group_data.task,
            )

            if has_errors:
                errors = True

    return errors


def _validate_tasks(
    template_path: str,
    filename: str,
    job_name: str,
    group_name: str,
    tasks: Sequence[Mapping[str, hcl2.Task]],
) -> bool:
    errors = False

    for task in tasks:
        for task_name, task_data in task.items():
            if not task_data.lifecycle and task_name != filename:
                errors = True
                _log_error(
                    (
                        '{0}: task "{1}" in group "{2}" in job "{3}" should be "{4}"'
                    ).format(
                        template_path,
                        task_name,
                        group_name,
                        job_name,
                        filename,
                    ),
                )

    return errors


def _expected_variables(
    variables: Sequence[Mapping[str, hcl2.Variable]],
) -> frozenset[str]:
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
    variables: Sequence[Mapping[str, hcl2.Variable]],
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
    print(msg, file=sys.stderr)  # noqa: T201,WPS421


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

        with open(template_path) as template_file:
            parsed = hcl2.loads(template_file.read())

            if _validate_jobs(template_path, filename, parsed.job):
                errors = True

            if _validate_variables(template_path, parsed.variable):
                errors = True

    return errors


if _main():
    sys.exit(1)
