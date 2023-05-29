# Visual Studio Code

Before you start, you need to export a Python virtual environment from Pants, as
well as the Python code generated from our protocol buffers.

```shell
pants export --resolve=python-default
pants export-codegen protobuf/::
```

You'll need to do this again whenever `vendor/constraints.txt` or a file in
`protobuf/` changes or your environment will quickly become outdated.

:::tip

You can use this extension [File Watcher](https://marketplace.visualstudio.com/items?itemName=appulate.filewatcher) to do this automatically.
After installing the extension add the following to the VS Code settings.json file *(this is typically found where VS Code is installed)*:
```
"filewatcher.commands": [
    {
        "match": "\\.proto*",
        "isAsync": true,
        "cmd": "cd '${workspaceRoot}'; pants export-codegen protobuf/::",
        "event": "onFileChange",
    },
    {
        "match": "vendor/constraints.txt",
        "isAsync": true,
        "cmd": "cd '${workspaceRoot}'; pants export-codegen protobuf/::",
        "event": "onFileChange",
    }
]
```
:::

### Configure Python Interpreter:

Once we have our environment exported, we need to configure VS Code to use the proper python interpreter.
:::note
*You'll need the Python extension installed if you don't already. See extensions section below*
:::

Locate the exported environment in `dist/export/python/virtualenvs/python-default/` and note the python version.

Open a terminal window and run `pyenv shell 3.11.3` - using the version found in the previous step!

Select View -> Command Palette (or Cmd+Shift+P) -> Python: Select Interpreter and select the new virtual env created by pyenv

Open a new terminal window and you should see it activate the python environment.

:::info
For whatever reason VS Code won't let you select the exported environment in `dist/export/...` as your python interpreter (which would be the ideal way to set up the project). So you'll need to use pyenv to create an environment in the proper python version and a slight workaround for resolving 3rd party imports (see below)
:::

### Resolve imports:

In order to resolve 3rd party imports simply use poetry (recommended) or even pip to install all the packages in our requirements.txt file.

In order for VS Code to be able to resolve relative imports throughtout the codebase you'll want to add the following to your VS Code settings.json file:
```
"python.analysis.extraPaths": [
    "${workspaceFolder}/python",
    "${workspaceFolder}/dist/codegen/python",
    "${workspaceFolder}/bash",
    "${workspaceFolder}/protobuf",
    "${workspaceFolder}/openapi"
]
```
:::note
*You'll need the Python extension installed for this setting if you don't already. See extensions section below*
:::

### Recommended Extensions:
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
- [Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
- [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
- [Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
- [File Watcher](https://marketplace.visualstudio.com/items?itemName=appulate.filewatcher)
- [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
- [OpenAPI (Swagger) Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi)
- [vscode-proto3](https://marketplace.visualstudio.com/items?itemName=zxh404.vscode-proto3)
- [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)

Some other recommended settings:
- **Format on Save** - add the following to VS Code settings.json: ```"editor.formatOnSave": true```
- **Python Default Formatter** - add the following to VS Code settings.json:
```
"[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
}
```
- **Exclude proto files from auto-formatting** - add the following to VS Code settings.json:
```
"[proto3]": {
    "editor.formatOnSave": false
}
```

:::tip

If you don't want these settings to apply to all workspaces and only to the specific workspace you are running Junction in, then put all these settings in a local dir.

Create a new folder called .vscode in the project root and create a new settings.json file. Put all your settings configs in this file and it will only apply to the current workspace.

:::

### Debugging Our Services

TBD!

Haven't been able to figure this one out yet...more to come

### And that's it, you should be all set up to run Junction! Happy Coding!

![](https://media.tenor.com/YvZwkF17Kn4AAAAC/good-job-leonardo-dicaprio.gif)
