# Junction Hub - Front End

This is a server side rendered SvelteKit application that allows users to interact with the Mobile API to book trips–and more.

## Onboarding

- Install [Homebrew](https://brew.sh/)

  - via [Snowfall's Engineering Onboarding resources](https://engineering.snowfalltravel.com/docs/monorepo/getting-started)

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

- Install a Node version manager that supports using the `.node-version` file. We recommend using [fnm](https://github.com/Schniz/fnm):

  ```bash
  brew install fnm
  ```

- Enable [`corepack`](https://nodejs.org/api/corepack.html) for Node. This will automatically install [Yarn](https://yarnpkg.com/) for you when you run it for the first time:

  ```bash
  corepack enable
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

# Running Tests

## Unit Tests

- Feel free to contribute and run unit tests:

```bash
yarn run test:unit
```

## E2E Tests

`Playwright` is an end-to-end test library designed to automate cross-browser web testing. `Playwright` supports all modern rendering engines including `Chromium`, `WebKit`, and `Firefox`.

### Run tests in the browser

```bash
yarn run test:e2e
```

This command will execute the tests as per the configuration in the `playwright.config.ts` file. Make sure your local development server (e.g., for SvelteKit) is running on `http://localhost:5173` when you execute the tests.

```bash
npx playwright test --headed
```

### Updating Playwright

```bash
yarn add -D @playwright/test@latest
```

# Useful Commands (MacOS)

## Clear Browser Cache

To see the most recent changes in your browser, you should clear your browser's cache or manually force refresh the website by using these keyboard shortcuts on your computer: The command will clear your web browser's cache:

```
[COMMAND] + [OPTION] + [E]
```

# Delete Browser Cookies

```
[COMMAND] + [SHIFT] + [DELETE]
```

## Reload Web Browser

```
[COMMAND] + R
```

- Note: this command only works on Safari browsers
