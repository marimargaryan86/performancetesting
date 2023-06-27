import asyncio
import sys

import aiofiles

from snowfall.stdlib.format import hcl2


def _log_error(msg: str) -> None:
    print(msg, file=sys.stderr)  # noqa: T201,WPS421


_CMD = " ".join(
    [
        "consul-template",
        "-dry",
        "-once",
        "-parse-only",
        "-template-error-fatal=true",
        "-template",
        "{0}",
        "-default-left-delimiter",
        "{1}",
        "-default-right-delimiter",
        "{2}",
    ],
)


async def _iterate_jobs(specification: hcl2.Specification, template_path: str) -> bool:
    errors = False

    for job in specification.job:
        for job_data in job.values():
            if await _iterate_groups(job_data, template_path):
                errors = True

    return errors


async def _iterate_groups(job: hcl2.Job, template_path: str) -> bool:
    errors = False

    for group in job.group:
        for group_data in group.values():
            if await _iterate_tasks(group_data, template_path):
                errors = True

    return errors


async def _iterate_tasks(group: hcl2.Group, template_path: str) -> bool:
    errors = False

    for task in group.task:
        for task_data in task.values():
            if await _iterate_templates(task_data, template_path):
                errors = True

    return errors


async def _iterate_templates(
    task: hcl2.Task,
    template_path: str,
) -> bool:
    errors = False

    for template in task.template:
        if await _validate_template(template, template_path):
            errors = True

    return errors


async def _validate_template(template: hcl2.Template, template_path: str) -> bool:
    async with aiofiles.tempfile.NamedTemporaryFile(
        "wb",
    ) as tmp_file:
        await tmp_file.write(
            template.data.replace(
                "${var.environment}",
                "foobar",
            ).encode(),
        )
        await tmp_file.flush()

        proc = await asyncio.create_subprocess_shell(
            cmd=_CMD.format(
                tmp_file.name,
                template.left_delimiter,
                template.right_delimiter,
            ),
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

        _, stderr = await proc.communicate()

        if stderr:
            _log_error(
                "{0}: {1}".format(
                    template_path,
                    stderr.decode().split(":", maxsplit=3)[3].strip(),
                ),
            )

        return bool(stderr)


async def _main() -> bool:
    if len(sys.argv) < 2:
        _log_error(
            "usage: {0} path/to/job.nomad path/to/job2.nomad".format(sys.argv[0]),
        )
        sys.exit(1)

    errors = False

    for template_path in sys.argv[1:]:
        async with aiofiles.open(template_path) as template_file:
            specification = hcl2.loads(await template_file.read())

        if await _iterate_jobs(specification, template_path):
            errors = True

    return errors


if asyncio.run(_main()):
    sys.exit(1)
