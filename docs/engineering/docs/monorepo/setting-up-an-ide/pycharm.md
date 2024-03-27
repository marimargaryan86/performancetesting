# PyCharm

Before you start, you need to export a Python virtual environment from Pants, as
well as the Python code generated from our protocol buffers.

```shell
pants export
pants export-codegen protobuf/::
```

You'll need to do this again whenever `vendor/constraints.txt` or a file in
`protobuf/` changes or your PyCharm environment will quickly become outdated.

:::tip

You can use [File Watchers](https://www.jetbrains.com/help/pycharm/using-file-watchers.html)
in PyCharm to do this automatically.

:::

Once we have our environment exported, we need to configure PyCharm to use it.
In your project settings, add `<path/to/project>/dist/export/python/virtualenvs/python-default/3.11.2/bin/python`
as the project interpreter.

:::info

Note that `3.11.2` in the path above could be different depending on what version of Python 3.11 you have installed.

:::

We now have to tell PyCharm about our folder structure. This is done by right-clicking
on each of the directories listed below and choosing the appropriate option under
"Mark directory as".

Sources Roots:
- `bash`
- `dist/codegen/python`
- `openapi`
- `protobuf`
- `python`

Excluded:
- `.pants.d`
- `.pids`

Namespace Packages:
- `python/snowfall`
