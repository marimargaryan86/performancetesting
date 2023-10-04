---
sidebar_position: 1
---

# Getting Started

## Prerequisites

The monorepo currently requires these tools to be installed and available in
your `$PATH`:

- [git](https://git-scm.com/)
- [jq](https://github.com/stedolan/jq)
- [Python](https://www.python.org/) (3.11.x)
- [scie-pants](https://github.com/pantsbuild/scie-pants)
- [npm](https://www.npmjs.com/) (For HUB)
- [yarn](https://yarnpkg.com/) (For HUB)

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
```

After installing `pyenv`, please [follow their instructions](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)
in order to configure it properly.

Once we have our tools installed, we need to install a Python interpreter. The
monorepo currently requires Python 3.11, so let's install that version through
`pyenv`:

```shell
pyenv install 3.11
```

## Clone the repo

Firstly, follow the `git` setup instructions [here](/docs/development/git).

The repository can then be cloned from GitLab with the following command:

```shell
git clone git@git.snowfall.se:junction/junction.git
```
