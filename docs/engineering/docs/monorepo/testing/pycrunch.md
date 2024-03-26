# PyCrunch

[PyCrunch](https://pycrunch.com) is a continuous testing tool for Python. It
will automatically run affected tests when code that the tests cover changes.

## Setup

### 1. Export dependencies

If the exported Python virtual environment are not up-to-date, export the latest
dependencies:

```shell
pants export
```

### 2. Configure PyCrunch Engine

PyCrunch requires a configuration file, `.pycrunch-config.yaml`, which has to be
placed in the repository root:

```yaml title=".pycrunch-config.yaml"
---
# documentation https://pycrunch.com/docs/configuration-file
engine:
  runtime: pytest
  enable-web-ui: false
  load-pytest-plugins: true
  change-detection-root: python/
  timeout: 15
discovery:
  exclusions:
    - .gitlab/
    - bash/
    - dist/
    - docs/
    - golang/
    - openapi/
    - protobuf/
    - python/snowfall/project/junction/api_automation/
    - svelte/
    - vendor/

```

We also need to make the `vendor/pyproject.toml` visible through auto-discovery,
which can be done by creating a symbolic link to it in the parent directory:

```shell
ln -s junction/vendor/pyproject.toml ../.
```

### 3. Install plugin

Currently, there only exists a PyCharm plugin. To install it, either go to the
[plugin homepage](https://plugins.jetbrains.com/plugin/13264-pycrunch--live-testing)
or search the PyCharm plugin marketplace for `pycrunch`. It requires no
additional configuration than what we have already done.

### 4. Starting the PyCrunch Engine

Open the PyCrunch toolbar, press the right-most button labeled "Run/Start
PyCrunch Engine", then manually run one or multiple test-suites that you want to
later be automatically trigger them for code changes. The gutter of the IDE will
automatically be populated with coverage information from now on.

### 5. Start coding

Whether you practice TDD or simply want to get immediate inline feedback from
existing tests while doing refactors, enhancing existing functionality or adding
new features, PyCrunch makes it all a little bit easier. No need to configure
additional run configurations in PyCharm, and no need to constantly switch to
your terminal to run `pants test ::` or similar.
