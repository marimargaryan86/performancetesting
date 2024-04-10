---
sidebar_position: 1
---

# Getting Started

## Prerequisites

The monorepo currently requires these tools to be installed and available in
your `$PATH` (installation notes by OS are included below the links):

- [git](https://git-scm.com/)
- [jq](https://github.com/stedolan/jq)
- [Python](https://www.python.org/) (3.11.x)
- [scie-pants](https://github.com/pantsbuild/scie-pants) (this is now the standard way of installing pants, so for MacOS `brew install pantsbuild/tap/pants`)
- [npm](https://www.npmjs.com/) (For HUB)
- [yarn](https://yarnpkg.com/) (For HUB)
- [xz](https://tukaani.org/xz/) (required for pants)
- [bash](https://www.gnu.org/software/bash/) (Bash version should be 4.0+)
- [docker](https://www.docker.com/)

Below follows instructions on how to install them on macOS.

### macOS

:::info

Please make sure you have [Homebrew](https://brew.sh/) installed before you start.

:::

:::caution

Some tools used by Pants currently don't support arm64 on macOS. So if you are
on a newer non-Intel Mac, make sure you have Rosetta installed:

```shell
softwareupdate --install-rosetta
```

:::

First you need to install the tools necessary to work in the monorepo. This is
done by running the follow commands in your terminal:

```shell
brew install git
brew install jq
brew install pantsbuild/tap/pants
brew install pyenv
brew install node
brew install yarn
brew install xz
brew install bash
brew install --cask docker
```

After installing `pyenv`, please [follow their instructions](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)
in order to configure it properly.

Once we have our tools installed, we need to install a Python interpreter. The
monorepo currently requires Python 3.11, so let's install that version through
`pyenv`:

```shell
pyenv install 3.11
```

:::info
Make sure you have **Docker** running in the background

`CMD + SPACE` and type "docker", then press enter to open Docker

or

Go to all applications, find and click on Docker to open it
:::

## Clone the repo

Firstly, follow the `git` setup instructions [here](/docs/development/git).

The repository can then be cloned from GitLab with the following command:

```shell
git clone git@git.snowfall.se:junction/junction.git
```

## Next Steps

Now that your environment is properly set up for development, we suggest you follow the following guides:

1. Setup your favorite IDE ([PyCharm](/docs/monorepo/setting-up-an-ide/pycharm) or [Visual Studio Code](/docs/monorepo/setting-up-an-ide/vscode)).
2. Understand the [high-level architecture of Junction](/docs/monorepo/architecture).
3. Take a [deep dive into the codebase](/docs/monorepo/code-deep-dive) to learn how the monorepo is organized.
4. Learn how to [run your first service](/docs/monorepo/running-a-service).
5. [Contribute to the monorepo](/docs/monorepo/contributing).
