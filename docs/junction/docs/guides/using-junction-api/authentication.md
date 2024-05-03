---
sidebar_position: 1
---

# Authentication

## Create an account

You need an account to be able to access the Junction API.

In your account creation e-mail you will find the following credentials which are required to generate your access token:
1. **OAuth Client ID** <small>(format: `uuid`)</small>
2. **OAuth Client Secret** <small>(format: `string`)</small>
3. **OAuth Token Endpoint URL** <small>(format: `string`)</small>

:::warning

Remember that your OAuth Credentials are a secret! Do not share them with others or expose it in any client-side code (browsers, apps).
:::

If you do not have these credentials or need help creating an account, contact us at: [support@snowfall.com]


## Generate an access token

Using your OAuth2 Client Credentials you will generate a JSON Web Token (JWT).

"Instructions here   ______     "


**All** of your **API requests** should include your API access token in an Authorization HTTP header as follows:

`Authorization: Bearer <YOUR_ACCESS_TOKEN>`

---

## Frequently asked questions

"Insert text here ________    "
