# Git

:::info

Please make sure you have [Homebrew](https://brew.sh/) installed before you
start.

:::

If not already installed, install git locally with:

```shell
brew install git
```

## Setup

### Identity

You can configure your git username and email with:

```shell
git config --global user.name "Your Name"
git config --global user.email your.email@snowfalltravel.com
```

### Editor

You should also set it to use your favorite text editor, so run either:

```shell
git config --global core.editor vim
```

or

```shell
git config --global core.editor <editor-name>
```

### Ignore

To always make sure you do not add any files that your operating system or IDE
creates you should always add a `.gitignore` to your `~/.gitconfig`. This kind
of information should ***never*** go into the repository root `.gitignore`.

Create the file `~/.gitignore` and add the appropriate files and folders to it
for [macOS](https://github.com/github/gitignore/blob/master/Global/macOS.gitignore),
after that add whatever your IDE creates, if you for example are using a
JetBrains product, add `.idea`.

After the `~/.gitignore` is complete, add it to your `~/.gitconfig` with:

```shell
git config --global core.excludesfile "~/.gitignore"
```

### SSH

To generate a new SSH key:

```shell
ssh-keygen -t ed25519 -C "your.email@snowfalltravel.com"
```

When you're prompted to "Enter a file in which to save the key", you can press Enter to accept the default file location. Default filename would be `id_ed25519`. Remember the filepath of where you saved it (usually current working directory).

For a more detailed instruction, read [external Github docs](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)


### Add SSH key to gitconfig

Edit the `~/.gitconfig` file with the editor of your choice.

Then add the following to the `[core]` section:

```
sshCommand = ssh -i ~/path-to-ssh-key/id_ed25519
```

### Add SSH to Gitlab account

Go to your Gitlab Preferences > SSH Keys > Add new Key

Copy your pub key:

```shell
pbcopy < ~/path-to-ssh-key/id_ed25519.pub
```

Now paste the pub key output into the text field and click Add key.

### Git Up

It's **highly** recommended to also add the `git up` alias, since this makes
pulling changes less painful:

```shell
git config --global alias.up "pull --all --autostash --prune --rebase --tags"
```

The command will do the following:

1. Create a temporary stash of your currently changed files.
2. Remove any remote-tracking references that no longer exist on the remote.
3. Fetch all remotes.
4. Fetch all tags from the remote.
5. Rebase the current branch on top of the upstream branch after fetching.
This keeps the history clean.
6. Pop the temporary stash and reapply your changes.

This greatly reduces the amount of conflicts and will help you keep a clean
commit history.

### Commands

There are only a handful of Git commands you should need to use during your
daily work, these are:

* `git status`
* `git diff`
* `git up`
* `git checkout`
* `git add`
* `git reset`
* `git commit`
* `git push`
* `git rebase`
* `git stash`

For more info on doing specific things, read the
[Git reference documentation](https://git-scm.com/docs).

## Branching

Within the Junction Monorepo, we
follow [Trunk Based Development](https://trunkbaseddevelopment.com/).

## Commits

Within the Junction Monorepo, we
follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary),
when you push to GitLab, you will receive errors if you do not follow this.

## Merge Requests

When raising a Merge Request (MR), please ensure that:

* The MR is a small as necessary to complete its related ticket
* Contains tests for new functionality or modified tests for changed functionality
* Your MR body briefly summarises the changes made
