---
sidebar_position: 3
---

# Using Pants

_To be written._

:::info

Pants' Go backend is currently disabled by default due its performance
implications. We're hoping to enable it by default again in the future.

To enable it, you need to configure Pants to use this additional
configuration file. This can be done by either setting an environment variable
or by passing a flag on the command line while running Pants.

```shell
PANTS_CONFIG_FILES="+['pants.go.toml']"
```

```shell
pants --pants-config-files="+['pants.go.toml']" ...
```

You can also copy the contents of `pants.go.toml` to a `.pants.rc` in the
repository root, but then you have to make sure that this file stays
up-to-date with any changes made to `pants.go.toml`.

:::
