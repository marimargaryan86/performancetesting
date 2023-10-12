# Integrating with Junction APIs

_WIP. This is a collection of observations a notes on how to use the various client-side services and utilites to integrate with Junction APIs._

## Models and Schemas

This application uses Zod for schema validation and type safety. 'Models' represent data in the shape of how `hub-web` uses it. 'Schemas' represent data in the shape of how server-side Junction services use it.

_NB: Don't confuse 'schemas' here for Zod schemas in general._

## Namespace Structure

The `integration` namespace provides baseline functionality for interacting with Junction services. These modules' sub-directories include:

- `parsers/` Functions that take data from API responses and parse them into models.
- `schemas/` Provides interfaces for converting data into `model`s or `schema`s.
- `services/` Services that make RESTful API requests to Junction endpoints.

### `common/`

Modules here provide reuseable functionality to build parsers, services, and schemas used to interact with specifc Junction services. _TBA._

### `junction-hub-api/`

Interacts with the Junction Hub API. Individual modules are named after their respective endpoints.

### `junction-mobile-api/`

Interacts with the Junction Mobile API. Individual modules are named after their respective endpoints.

### `ory/`

Interacts with the Junction-ORY integration. Provides helpers for authentication flow.

---

## Notes

Work in progress.

- Services handle API calls
- Abstract classes provide structure and customization to HTTP requests to respective services
- Individual services named after their endpoints conatin CRUD methods that actually make HTTP requests
