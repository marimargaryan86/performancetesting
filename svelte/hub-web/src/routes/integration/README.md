# `routes/integration` middlewares

## Summary

These middlewares bridge the needs of both SvelteKit SSR routing & `fetch` paradigms and our Junction Services OpenAPI & JSONSchema specifications. Our SvelteKit server must intercept RESTful requests from the browser and apply transformations before routing them elsewhere. Modules in this directory parse browser requests, marshall client data into requests that Junction can understand, gets or sets data from our cookie store, then finally passes them to the correct `IntegrationInstance` service.

Feel free to reach out for assistance in navigating, developing, debugging, or refactoring inside of this directory.
