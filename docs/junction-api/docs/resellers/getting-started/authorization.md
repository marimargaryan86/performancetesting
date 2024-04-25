---
sidebar_position: 1
---

# Authorization

## Pre-requisites

1. **OAuth Client ID** <small>(format: `uuid`)</small>
2. **OAuth Client Secret** <small>(format: `string`)</small>
3. **OAuth Token Endpoint URL** <small>(format: `string`)</small>

If you do not have any of these, please contact us via [Slack](https://snowfalltravel.com/contact)!

---

## OAuth Client Token

Once we have provided you with OAuth2 Client Credentials during your onboarding, you
may use this with instructions we'll provide to generate your **access token**, which can be used to make requests to our API.

### What are these access tokens?

They are JSON Web Tokens (JWTs), which are a widely used format for representing claims securely between parties. They can be used as access tokens, which are used to grant access to protected resources, such as APIs.

### What to do with the access token

**All** of your **API requests** should include your API access token in an Authorization HTTP header as follows:

`Authorization: Bearer <YOUR_ACCESS_TOKEN>`

:::warning

Remember that your OAuth Credentials are a secret! Do not share them with others or expose it in any client-side code (browsers, apps).
:::

Don't worry if you don't know how to use it, we'll show you in the [**Quickstart**](/docs/resellers/getting-started/quickstart).

---

## Extras

You can use the following tools to help make API requests:

- Postman [*(link)*](https://www.postman.com/)

- Python [*(link)*](https://www.python.org/)
    - Requests library [*(link to docs)*](https://requests.readthedocs.io/en/latest/)
