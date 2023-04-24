---
sidebar_position: 1
---

# Getting Started

The repository can be cloned from GitLab with the following command:

```shell
git clone git@git.snowfall.se:junction/junction.git
```

## Prerequisites

The monorepo currently requires these tools to be installed and available in
your `$PATH`:

- [jq](https://github.com/stedolan/jq)
- [Python](https://www.python.org/) (3.11.x)
- [scie-pants](https://github.com/pantsbuild/scie-pants)

Below follows instructions on how to install them on Linux as well as on macOS.


### Linux

_Not yet written. Feel free to send a merge request!_

### macOS

:::info

Please make sure you have [Homebrew](https://brew.sh/) installed before you start.

:::

First you need to install the tools necessary to work in the monorepo. This is
done by running the follow commands in your terminal:

```shell
brew install jq
brew install pantsbuild/tap/pants
brew install pyenv
```

After installing `pyenv`, please [follow their instructions](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)
in order to configure it properly.

Once we have our tools installed, we need to install a Python interpreter. The
monorepo currently requires Python 3.11, so let's install that version through
`pyenv`:

```shell
pyenv install 3.11
```

:::caution

Some tools used by Pants currently don't support arm64 on macOS. So if you are
on a newer Mac, make sure you have Rosetta installed:

```shell
softwareupdate --install-rosetta
```

:::

### Microsoft Windows

Microsoft Windows is not supported by Pants at this time, but you could probably
get it to run under the Windows Subsystem for Linux (WSL). Please refer to [their
documentation](https://www.pantsbuild.org/docs/prerequisites#microsoft-windows)
for more information.
