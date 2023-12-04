# Junction Hub - Front End

This is a server side rendered SvelteKit application that allows users to interact with the Mobile API to book trips–and more.

## Onboarding

- Install [Homebrew](https://brew.sh/)
  - via [Snowfall's Engineering Onboarding resources](https://engineering.snowfalltravel.com/docs/monorepo/getting-started)
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Install [Node.js](https://nodejs.org/en), preferably a long term support version
  - Node Version Manager, [nvm](https://github.com/nvm-sh/nvm) is recommended
- Install [Yarn package manager](https://yarnpkg.com/)
  ```bash
  brew install yarn
  ```
- Sign up for ORY `dev` environment credentials [here](https://exciting-boyd-kr7iwir8gj.projects.oryapis.com/ui)
- (_Optional_) Install ORY client
  ```bash
  brew install ory/tap/cli
  ```

## Running a local `hub-web` development instance

1. Navigate to the `hub-web` directory.

```bash
cd svelte/hub-web
```

2. Create an environmental variables file. Refer to the existing `svelte/hub-web/.env.example` file for configuration. Contact another developer on the team to populate it with the correct configuration variables.

```bash
touch .env
```

```bash
# .env.example

BOOKING_HUB_API_BASE_URL=https://example.com
HUB_API_BASE_URL=https://example.com
PUBLIC_STRIPE_KEY=token
PUBLIC_SENTRY_DSN=sentry-dsn
SENTRY_ORG=myorg
SENTRY_PROJECT=myproject
SENTRY_AUTH_TOKEN=authtoken
SENTRY_URL=https://example.com
ORY_BASE_URL=https://example.com

```

3. (_Optional_) Open a terminal and run an ory development instance:

```bash
ory tunnel --dev --project exciting-boyd-kr7iwir8gj http://localhost:4000
```

- **production**: `optimistic-tereshkova-36hc6vayw4`
- **dev**: `exciting-boyd-kr7iwir8gj`
- **sandbox**: `hardcore-nash-njumtzes9i`

  _Alternatively, you may point your `.env` file to a deployed ORY instance._

4. Open a separate terminal instance and install dependencies:

```bash
yarn install
```

4. After install, stand up a local server:

```bash
yarn run dev
```

5. Sign in on your Snowfall VPN.
6. Sign into the `hub-web` app using your ORY credentials.

## Notes

- Please format, lint, and check before committing:

```bash
yarn run format
yarn run lint
yarn run check
```

- Feel free to contribute and run unit tests:

```bash
yarn run test:unit
```
