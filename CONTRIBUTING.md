# How to Contribute

## MacOS Development

### Set up your local environment

1. Install [pyenv][pyenv].
```shell
brew install pyenv
```
2. Add the pyenv shims (`$(pyenv root)/shims`) to your `PATH` by adding the following to your dotfiles.
```shell
export PATH="$(pyenv root)/shims:$PATH"
```
3. Install [Docker][docker].
```shell
brew install docker
```
4. If you are on a Mac with an arm64 processor, make sure you have Rosetta installed.

### Set up the Junction environment

1. Clone the [Junction repository][junction-repo] and navigate to the `junction` directory.
```shell
git clone git@git.snowfall.se:junction/junction.git
cd junction
```
2. Install the correct Python interpreter using `pyenv`. It will automatically install the version specified in the `.python-version` file.
```shell
pyenv install
```

### Set up your IDE (Optional)

1. Export the virtual environment using Pants.
```shell
./pants export ::
```
2. Export generated code using Pants.
```shell
./pants export-codegen ::
```

#### PyCharm

1. In your project settings, add `dist/export/python/virtualenvs/python-default/3.9.10/bin/python` as the project interpreter.
2. Mark the following paths as (right click on folder + mark directory as):
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

## Testing

There are a few [Pants][pants] commands that you will be using for linting, testing and type-checking.

```shell
./pants lint ::
./pants test ::
./pants check ::
./pants tailor --check
./pants update-build-files --check
```

A helpful command to run all the things that will be checked in the pipeline that can be added as an alias is:
```shell
./pants tailor --check update-build-files --check && ./pants fmt lint --changed-since=main && ./pants --changed-since=main --changed-dependees=transitive check test
```

## Development

### Code Style

This project uses Black to format the code, Mypy for type checking and flake8
for linting.

We follow rules of [wemake-python-styleguide][wemake-python-styleguide],
except in a few cases where it collides with Black or causes difficulties with
writing unit tests.

Try and use imports that follow Google's [Python styleguide][google-styleguide].

### Comments In Code

Avoid comments in code. Check [Uncle Bob's video on the subject][uncle-bob-video]
or check [the written summary][uncle-bob-summary].

### Working With Dependencies

#### Adding Dependencies

1. Add the dependency and its version to `vendor/requirements.txt`.
2. Run `./pants --no-pantsd generate-lockfiles --resolve=python-default`.
3. If the dependency's requirement name and the module name is different, or if
   the requirement exposes additional modules, the dependency and its modules
   needs to be added to `module_mapping` in `vendor/BUILD`.

#### Updating Dependencies

1. Update the dependency's version in `vendor/requirements.txt`.
2. Run `./pants --no-pantsd generate-lockfiles --resolve=python-default`.

#### Removing Dependencies

1. Remove the dependency from `vendor/requirements.txt`.
2. Run `./pants --no-pantsd generate-lockfiles --resolve=python-default`
3. If the dependency has been added to `module_mapping` in `vendor/BUILD`, make
   sure to remove it.

### Creating A New Service

The minimum code for a new service is:

```python
from snowfall.stdlib import service


class _Settings(service.Settings):
    foobar: str


async def _method(app: service.Application[_Settings]) -> None:
    """Your code here."""


if __name__ == "__main__":
    entrypoint = service.new_entrypoint(
        name="service_name",
        commands=(
            service.new_command(
                name="command_name", callback=_method, settings_class=_Settings
            ),
        ),
    )

    service.invoke(entrypoint)
```

### Making Commits

This repository follows [Conventional Commits][conventional-commits] for its commits. The following types are accepted:

- `build` - changes to Pants, Dockerfiles etc.
- `chore` - mundane tasks like updating dependencies etc.
- `ci` - changes to the GitLab pipeline, Nomad deploys etc.
- `docs` - documentation related changes
- `feat` - new features
- `fix` - bug fixes
- `perf` - performance related changes and refactors
- `refactor` - general refactors
- `revert` - code and commit reverts
- `style` - code style changes
- `test` - test related changes

There are also various optional [scopes][junction-scopes] that can be added to the commit message to further categorize the commit.

## Running Services

It's generally favorable to run services through Pants (either in your IDE or terminal of choice) to get a more production-like experience, but running them through Python by exporting a virtual environment from Pants is also possible.

Regardless of method, you need to run `docker compose up` to boot up all required third-party services. Also remember that some first-party services have dependencies on other first-party services.

### Command Line

#### Pants

```shell
bash bash/run.sh python/snowfall/junction/{service} {task}
```

### PyCharm

#### Pants

1. Under `Run`, click `Edit Configurations`.
2. Click `Add New Configuration` and then `Shell Script`.
3. Set `Script path` to `{repository path}/junction/bash/run.sh`.
4. Set `Script options` to the path to the service you want to configure as well as the task you want to run, e.g. `python/snowfall/junction/echo/main.py grpc`.
5. Make sure `Interpreter path` is set to a **Bash** shell.
6. Make sure `Execute in the terminal` is _unchecked_.

#### Python

1. Make sure the [EnvFile plugin][envfile-plugin] is installed.
1. Under `Run`, click `Edit Configurations`.
3. Click `Add New Configuration` and then `Python`.
4. Make sure it says `Module Name` and not `Script Path`, change if necessary.
4. Set the `Module Name` to the service you want to configure, e.g. `snowfall.junction.echo.main`.
5. Set the `Parameters` to the task you want to run, e.g. `grpc`.
6. Set the `Working directory` to `{repository path}`.
7. Click `EnvFile` submenu, check `Enable EnvFile` and `Add` a new .env file path to the service's .env.dist file (or .env if you've made local changes), e.g. `{repository path}/python/snowfall/junction/echo/.env.dist`.

# M1 troubleshooting
- install xcode
- install openssl
```
brew install openssl@3
```
and follow instructions for setting appropriate environment variables (in the output of the `brew install` command).
- install llvm (for python rapidjson package)
```
brew install llvm
```
and follow instructions for setting appropriate environment variables (in the output of the `brew install` command).
- install rust (for python cryptography package)

# FAQ
## When running a service Settings are not being loaded properly, e.g. `amqp_dsn field required (type=value_error.missing)`.

Make sure to set the environment variables in `.env.dist` in every service folder.
If you're using `fish shell` you must add `-x` option to the `set` command, otherwise the variables are only set locally.

[pants]: https://pantsbuild.github.io/
[docker]: https://www.docker.com/
[pyenv]: https://github.com/pyenv/pyenv
[junction-repo]: https://git.snowfall.se/junction/junction
[google-styleguide]: https://google.github.io/styleguide/pyguide.html#22-imports
[wemake-python-styleguide]: https://wemake-python-stylegui.de/en/latest/
[uncle-bob-video]: https://youtu.be/2a_ytyt9sf8?t=296
[uncle-bob-summary]: https://bpoplauschi.github.io/2021/01/20/Clean-Code-Comments-by-Uncle-Bob-part-2.html
[envfile-plugin]: https://plugins.jetbrains.com/plugin/7861-envfile
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[junction-scopes]: https://git.snowfall.se/junction/junction/-/labels?subscribed=&search=scope%3A%3A
