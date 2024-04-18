# Snowman

## Introduction

Snowman is a GitLab bot developed internally at Snowfall with its source code
available in [the monorepo](https://git.snowfall.se/junction/junction/-/tree/main/golang/cmd/snowman?ref_type=heads). The goal
of Snowman is to enforce and automate a standardized GitLab workflow throughout
the organization.

## Installation

In order to install Snowman in a GitLab project, you need to invite the
[Snowman GitLab user](https://git.snowfall.se/snowman) and give it (at least)
the `Maintainer` role. Snowman checks for new projects periodically and will,
once invited, be enabled within the next ten minutes.

## Configuration

Some of Snowman's features and functionality can be tweaked by adding a
`.snowman.yml` file to the root of your repository.

### Default Configuration

```yaml
---
commits:
  scopes: null
  types:
    - build
    - chore
    - ci
    - docs
    - feat
    - fix
    - perf
    - refactor
    - revert
    - style
    - test
metrics:
  base_size: 200
  growth_rate: 2
reviewers:
  blacklist: null
  breaking: null
stale_branches:
  should_delete: false
  activity_threshold: 2160h0m0s
use_merge_train: false
```
