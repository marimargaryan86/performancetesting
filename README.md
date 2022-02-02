# Junction

Junction is a mono-repository that is using [Poetry][poetry] for dependency
management and [Pants][pants] for tooling, like linting, testing, type-checking
and building.

# Setup

1. Install [Poetry][poetry] (at least `1.2.0a2`), [Docker][docker] and
   [pyenv][pyenv].
2. Run `pyenv install`. It will automatically install the version specified in
   the `.python-version` file.
3. Install dependencies by navigating to `/vendor` and run `poetry install`.
   Remember the interpreter path that Poetry generates.
4. Run `./pants export-codegen ::` to generate required code.

## PyCharm

1. Install the EnvFile plugin.
2. In your project settings, add the interpreter path from Poetry as the project
   interpreter.
3. Mark the following paths as:
   1. Source Folders:
      1. `dist/codegen/python`
      2. `python`
      3. `bash`
      4. `protobuf`
      5. `openapi`
   2. Excluded Folders:
      1. `.pants.d`
      2. `.pids`
   3. Namespace Package Folders:
      1. `python/snowfall`

# Running Services

1. Run `docker compose up` to start the required dependencies.

## IDEs

### PyCharm (recommended)

Setup your Run/Debug configurations:

1. Set the Module Name to`snowfall.junction.{service}.main`.
2. Set the Parameters to the task you want to run (like `serve`).
3. Set the working directory to the Junction root folder.
4. Add the respective service's `.env.dist` file to EnvFile configuration.

Now you can just run the service you want to start, but remember that some
services might depend on other services.

## Command Line

When running a service by command line, you have to make sure you load the
service's `.env.dist` file, just like if you were using an IDE.

### Pants

1. Run `./pants run /python/snowfall/junction/{service}/: -- {task}`.

### Python

1. Run `{path-to-the-poetry-python-environment} -m snowfall.junction.{service}. main {task}`

# Development

## Code Style

This project uses Black to format the code, Mypy for type checking and flake8 for linting.

We follow rules of [wemake-python-styleguide][wemake-python-styleguide],
except in a few cases where it collides with Black or causes difficulties with
writing unit tests.

Try and use imports that follow Google's [Python styleguide][google-styleguide].

## Comments In Code

Avoid comments in code. Check [Uncle Bob's video on the subject][uncle-bob-video]
or check [the written summary][uncle-bob-summary].

## Working With Dependencies

### Adding Dependencies

1. Navigate to `/vendor` and run `poetry add {package}`.
2. Make sure the packages in `pyproject.toml` are in alphabetic order.
3. Run `poetry export --without-hashes --dev -o lock/constraints.txt`.

### Updating Dependencies

1. Navigate to `/vendor` and run `poetry update`.
2. Run `poetry export --without-hashes --dev -o lock/constraints.txt`.

### Removing Dependencies

It's problematic to remove dependencies, because `poetry remove {package}`
uninstalls more than just the package. Think about if you have to install a
package before doing it.

## Creating A New Service

The minimum code for a new service is:

```python
from snowfall.service import RunnableService, Task, make_runnable_service

async def _task_method(service: RunnableService) -> None:
    """Your code here."""

if __name__ == "__main__":
    _service = make_runnable_service(
        name="service_name",
        tasks=(Task(command="task_name", method=_task_method),),
    )
    _service.run()
```

[poetry]: https://python-poetry.org/
[pants]: https://pantsbuild.github.io/
[docker]: https://www.docker.com/
[pyenv]: https://github.com/pyenv/pyenv
[google-styleguide]: https://google.github.io/styleguide/pyguide.html#22-imports
[wemake-python-styleguide]: https://wemake-python-stylegui.de/en/latest/
[uncle-bob-video]: https://youtu.be/2a_ytyt9sf8?t=296
[uncle-bob-summary]: https://bpoplauschi.github.io/2021/01/20/Clean-Code-Comments-by-Uncle-Bob-part-2.html
