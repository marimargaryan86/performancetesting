# Hub UI (Front-End)

## Frontend Development

Hub is a server side rendered SvelteKit application that allows users to interact with the Mobile and Hub APIs to book trips, review orders, and more.

> [Junction Hub](https://hub.junction.dev/) is developed with SvelteKit, an innovative framework designed for building web applications.

### SvelteKit

Broadly speaking, Hub uses Sveltekit to create a MVC-style backend framework which uses Svelte as its "View" layer. Specific pages or `routes` are server-side rendered statically at the top level with child components being client-side rendered as needed.

> SvelteKit leverages a variety of features designed for modern web development, such as the following:
>
> * Filesystem-Based Routing: An intuitive and efficient way to manage routes through a simple file structure.
> * Server-Side Rendering (SSR): Enhances performance and SEO by rendering pages on the server before they reach the user.
> * Page-Specific Rendering Modes: Offers flexibility in how each page is rendered, catering to diverse content needs.
> * Offline Support: Ensures a seamless user experience even in situations with limited or no internet connectivity.
>
> SvelteKit's toolkit accelerates the development process, enabling us to deliver a more dynamic and responsive user interface in Junction Hub.
>

:::tip

To delve deeper into the capabilities and advantages of SvelteKit, we encourage exploring its [official tutorial](https://learn.svelte.dev/tutorial/welcome-to-svelte) and [documentation](https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/Svelte_getting_started)._

:::

## 1. Prerequisites

### Homebrew

Begin by installing [Homebrew](https://brew.sh/)
* Follow the steps provided in [Snowfall's Engineering Onboarding resources](https://engineering.snowfalltravel.com/docs/monorepo/getting-started).
* Run the installation script:

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

### Node.JS

Install [Node.js](https://nodejs.org/en).

:::tip

Preferably a long term support version. We recommend using [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm) for managing Node.js versions.

:::

### Yarn Package Manager

* Install the [Yarn package manager](https://yarnpkg.com/):

  ```bash
  brew install yarn
  ```

## 2. User Registration

### Register Ory Account

:::info

Sign up for ORY dev environment credentials [here](https://exciting-boyd-kr7iwir8gj.projects.oryapis.com/ui).

:::

## 3. Configure Environment Variables

### Create .env file

Navigate to the `hub-web` directory.

  ```bash
  cd svelte/hub-web
  ```

#### Add Environment Variables

Populate the .env file using `svelte/hub-web/.env.example` as a reference.

  ```bash
  touch .env
  ```

#### Example .env content

:::tip

Consult a team member for specific values

:::

  ```.env
  BOOKING_HUB_API_BASE_URL=<https://example.com>
  HUB_API_BASE_URL=<https://example.com>
  PUBLIC_STRIPE_KEY=token
  PUBLIC_SENTRY_DSN=sentry-dsn
  SENTRY_ORG=myorg
  SENTRY_PROJECT=myproject
  SENTRY_AUTH_TOKEN=authtoken
  SENTRY_URL=<https://example.com>
  ORY_BASE_URL=<https://example.com>
  ```

#### Run Development Servers

For local development, enable the development mode:

  ```bash
  ory tunnel --dev --project exciting-boyd-kr7iwir8gj http://localhost:4000
  ```

* **production**: `optimistic-tereshkova-36hc6vayw4`
* **dev**: `exciting-boyd-kr7iwir8gj`
* **sandbox**: `hardcore-nash-njumtzes9i`

:::tip

_Alternatively, you may point your `.env` file to a deployed ORY instance and skip this step._

:::tip

## 4. Install Dependencies

Inside of the hub project directory `svelte/hub-web/` install project dependencies:

  ```bash
  yarn install
  ```

#### Run Development Server

Then, open a new terminal and start a local development server:

  ```bash
  yarn run dev
  ```

## 5. Staging Changes

Ensure code quality by formatting, linting, and running checks before commits:

  ```bash
  yarn run format
  yarn run lint
  yarn run check
  ```
