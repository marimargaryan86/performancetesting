# Third-Party Dependencies

## Adding Dependencies

When adding a new dependency, always check the current list of dependencies to
see if there's already a dependency that can do what you need. As an example we
have already decided to use `httpx` for making HTTP requests in Python, so you
should use that instead of also adding `aiohttp` or `requests` to our list
dependencies.

It's also a good idea to check the health of the dependency. When was it last
updated, how many stars does it have on GitHub, etc. If it's a tiny dependency that
hasn't been updated in years, it's worth considering writing it ourselves instead.

### Go

_To be written._

### Python

Add the dependency and its **exact** version to `vendor/requirements.txt` and run:

```shell
pants generate-lockfiles --resolve=python-default
```

:::info

If the dependency exposes a module different from its project name, or if the
dependency exposes additional modules, the dependency and its modules needs to
be added to `module_mapping` in `vendor/BUILD`.

See the [Pants documentation](https://www.pantsbuild.org/docs/python-third-party-dependencies#use-modules-and-module_mapping-when-the-module-name-is-not-standard)
for more information.

:::

## Updating Dependencies

### Go

_To be written._

### Python

Update the dependency's version in `vendor/requirements.txt` and run:

```shell
pants generate-lockfiles --resolve=python-default
```

## Removing Dependencies

### Go

_To be written._

### Python

Remove the dependency from `vendor/requirements.txt` and run:

```shell
pants generate-lockfiles --resolve=python-default
```

:::info

Make sure to remove the dependency from `module_mapping` and `overrides` in
`vendor/BUILD` as well if it has any configuration there.

:::
