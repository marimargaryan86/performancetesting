---
sidebar_position: 2
---

# Authorization

Currently we're supporting two methods to access Go's main API (Reseller API).

1. **JSON web tokens [jwt.io](https://jwt.io/)**

This is our legacy authentication method, using a defined public and private key.
You should use one of these when doing your **local development**. We have a runnable
script [here](https://git.snowfall.se/junction/junction/-/blob/main/python/snowfall/project/junction/go/service/client_api/jwt_generator.py)
which will print out a JWT to use with the API.

2. **OAuth2 via [Ory](https://www.ory.sh/)**

We use authorization through [Ory's OAuth2](https://www.ory.sh/docs/oauth2-oidc/)
for API access from external services, i.e. our other services or customers
integrating with the Reseller API. The guide below explains how this is done.

---

## OAuth Guide

### Pre-requisites

1. **OAuth Client ID** <small>(format: `uuid`)</small>
2. **OAuth Client Secret** <small>(format: `string`)</small>
3. **OAuth Token Endpoint URL** <small>(format: `string`)</small>

### OAuth Client Token

Once we have provided a customer with OAuth2 Client Credentials during their
onboarding, they can use these instructions to generate an **access token**,
which can be used to make requests to our API.

### What are these access tokens?

They are JSON Web Tokens (JWTs), which are a widely used format for representing claims securely between parties. They can be used as access tokens, which are used to grant access to protected resources, such as APIs.

### What to do with the access token

**All** of your **API requests** should include your API access token in an Authorization HTTP header as follows:

`Authorization: Bearer <YOUR_ACCESS_TOKEN>`
