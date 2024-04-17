# Contributing

We enforce coding standards on all code commited to the monorepo. Before
raising your first merge request, take some time to familiarize yourself with
[our development practices](/docs/development).

The general process for getting new code accepted is:

1. Create a Merge Request (MR) with your changes.
2. Get the required approvals:
    * From one of your peers. This might require addressing comments from that
      person.
    * From snowman, which will auto-approve once all [CI/CD pipelines](/docs/development/ci-cd)
      are passed.
3. The code is automatically merged and deployed.

We follow [trunk-based development](https://trunkbaseddevelopment.com/), so we
aim to merge code as often as possible and not maintaining long-living
branches. The general advice is to merge incremental improvements as early and
as often as possible. Avoid very large MR and instead do small and focused MR
that improves one aspect, get it reviewed and merge, and keep building on top
of it.

## Create a Merge Request (MR)

Prerequisites: You have checked out a clean `main` branch, no local changes.

1. Pull the repository:

    ```shell
    git pull
    ```

2. Create a local working branch (use any name, but must be globally unique):

    ```shell
    git checkout -b your-new-branch
    ```

3. Apply your changes. Keep your change as small as possible and focused on
just one goal.

4. Commit your changes, make sure to follow [our commit guidelines](/docs/development/git#commits):

    ```shell
    git add .
    git commit -m "<type>[optional scope]: <description>"
    ```

    This repository follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for its commits. The following types are accepted:

    * `build` - changes to Pants, Dockerfiles etc.
    * `chore` - mundane tasks like updating dependencies etc.
    * `ci` - changes to the GitLab pipeline, Nomad deploys etc.
    * `docs` - documentation related changes
    * `feat` - new features
    * `fix` - bug fixes
    * `perf` - performance related changes and refactors
    * `refactor` - general refactors
    * `revert` - code and commit reverts
    * `style` - code style changes
    * `test` - test related changes

5. Push your branch:

    ```shell
    git push origin your-new-branch
    ```

    This will return a link in the terminal that you can follow to create the MR.

6. Create the MR with gitlab interface.

    At this point, you can choose a reviewer. Feel free to select anyone you
    think should review the MR. If you don't select anyone, the snowman bot will
    automatically assign somebody.

    :::info

    Some areas of the monorepo requires specific owner approval, if you are
    changing a file, you can generally get an initial approval from any
    colleague, and then snowman will automatically assign an additional
    reviewer that has the ownership over the code to double check the MR.

    :::

7. Once you have all the approvals, snowman will automatically merge your MR.
Good job!

This process (along with good git practices) is presented in [this
video](https://drive.google.com/drive/folders/1i5BdD4Ut76jee5kslsaeMaxDSzHAQzuc).
