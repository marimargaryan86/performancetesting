# Localization

## Context

The current implementation of localization is a stop gap until we can get Locize up and running.

## Summary

The `/lang` directory contains locale dictionaries stored as JS objects for the various languages `hub-web` supports. The `index.ts` is a Svelte store that allows the SvelteKit server to access the cutenr locale and its respective dictionary. This implementation preserves SSR for the app.

### Details

> [_This_] implements a mechanism for tracking the selected locale (via a cookie) and then utilizes a SvelteKit hook to ensure that it's part of `app.locals`. In the topmost server-layout, the appropriate language data is loaded (so we don't bloat FE with all translations), it is then passed to the layout page which creates a context using helper methods for `locale` and `locale-data` which are saved as two separate stores. These can then be accessed throughout the app via `getLocaleData` (readonly store) and `getLocale()` (writable store). Whenever the store from `getLocale()` is updated, the topmost layout will update the locale cookie and trigger `invalidateAll()`; the rest is handled by the **hook** -> **layout** -> **context** pipeline I just described. [_This approach was chosen because_] it would be a bit problematic to load all language sets and send them to the client. It also allows for SSR.

## Moving Forward

Eventually, the locale info will be stored in a deployed Locize service that provides an admin GUI for developers and translators to work out of. We'll implement a system that pulls down the correct locale file and, ideally, refactor the store to use it.
