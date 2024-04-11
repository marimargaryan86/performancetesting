# Acceptance Tests for Junction API

## Introduction

These Acceptance tests are designed to validate the functionality of
our public-facing Junction API from the perspective of
an end-user.

Running post-merge in our Continuous Deployment (CD) pipeline,
these tests ensure that our core paths for product and business validation are
checked across all travel verticals (air, car rental, rail, hotel,
and ferry).

### Mocked / Deterministic

To ensure reliability of our deployment pipeline, these tests run against
mocked versions of external services to ensure deterministic and stable
results. Any failure in these tests could potentially block deployment to live
environments, emphasising the importance of their stability.

Our design is based on a service object model, allowing us to
encapsulate and manage the complexities of API interactions within well-defined
objects. This model aids in creating more readable, maintainable, and scalable
tests as we extend our platform's capabilities.

For questions on contributing or for assistance, please join our
[Slack channel: #squad-qa](https://snowfall.slack.com/archives/C05F3FJ57AA).

## Prerequisites / Setup

* See CONTRIBUTING.md for junction project setup with pants

- **Allure for reporting**: Ensure Allure is installed on your system to
  generate and view test reports (`brew install allure`)

## How to Run Tests

### Command Line Arguments

There are various args needed to run the tests.

#### Pytest Marker

Tests are marked with the pytest marker verify.

```
-m verify
```

#### Allure

Allure is used for reporting and must be pre-installed (`brew install allure`)

```
--alluredir=/tmp/allure-report
```

To view results run the following in a terminal:

```
allure serve /tmp/allure-report
```

This will open the Allure report in a new browser tab.

#### Mocked Token (as CD)

The default execution is against mocks controlled via a long-lived token/auth,
and is also against the dev environment deployment.

The app base url and tokens are stored in vault and host url and token for
the vault must be provided:

```
--API-TOKEN="ADD VAULT TOKEN HERE"
--HOST="ADD VAULT URL HERE"
```

#### Running Locally

If you wish to run against a local url then you can override using dev by using
the arg below instead:

```
--LOCAL_API_URL='http://localhost:8000'
```

#### Using a different token (non-mocked) via Ory

If you wish to run against a non-mocked back end (or for other reasons) you can
get a just-in-time token via Ory. You need to set the Ory url and supply your
basic token.

**Note**: you must cannot use with vault args above, so you must also set
LOCAL_API_URL

```
--BASIC_TOKEN="ADD BASIC TOKEN HERE"
--ORY_URL='https://exciting-boyd-kr7iwir8gj.projects.oryapis.com/oauth2/token'
```

### Examples

Here are some typical usages or args all together.

#### Running Tests in PyCharm

To run & debug in Pycharm update your:
`Run/Debug Configuration/Additional Arguments`.

```
-m verify
--alluredir=/tmp/allure-report
--API-TOKEN="ADD VAULT TOKEN HERE"
```

Tests live under:

```
python/snowfall/project/junction/api_automation/junction_api_tests/
```

So you can run all from the root above, of specific files and tests per
vertical. For example, air vertical tests are in `air_test.py`.

### Running Tests via Pants (dev env)

```
pants test --force --output=all
python/snowfall/project/junction/api_automation/junction_api_tests/::
--pytest-args='-m verify'
-- --alluredir=/tmp/allure-report
--API-TOKEN="ADD VAULT TOKEN HERE"
--HOST="ADD VAULT URL HERE"
```

### Running Tests via Pants (local env)

```
pants test --force --output=all
python/snowfall/project/junction/api_automation/junction_api_tests/::
--pytest-args='-m verify'
-- --alluredir=/tmp/allure-report
--ORY_URL="https://exciting-boyd-kr7iwir8gj.projects.oryapis.com/oauth2/token"
--BASIC_TOKEN="ADD BASIC TOKEN HERE"
--LOCAL_API_URL='http://localhost:8000'
```

## Postman

To enable exploration of the Junction API endpoints we have postman collections
that can be used in `dev`.

These have basic examples for each vertical and endpoints.

**Note**: while we try to maintain the collections they may become out-of-date
with the deployed `dev` environment.

### Chained requests

To save on copy and pasting id's, the collections have been coded to extract
search id's, etc... to then use in subsequent queries.

This enables running the requests in order without effort. However, if you need
want to test/check a specific search id, for example, you can replace a variable
with a hard coded value.

### Authentication / Access

All requests use the `bearer_token` for authentication.

#### Long-lived token

In QA we used a long-lived token that can be copied in once. This enables us to
test against a mocked backend.
Update the `bearer_token` manually in the dev environment.

Please message in the qa channel to get this token:

[Slack channel: #squad-qa](https://snowfall.slack.com/archives/C05F3FJ57AA).

#### Just-in-time token

If you want to use `dev`, not against mocked environment, with your own
basic token, you can update the `basic_token` and `ory_url` variables.

Once updated, execute the` Ory Auth/Token // Get Bearer Token `request. This
will automatically update the `bearer_token` used in requests.

Please message in the qa channel if you need a `basic_token` and `ory_url`:

[Slack channel: #squad-qa](https://snowfall.slack.com/archives/C05F3FJ57AA).
