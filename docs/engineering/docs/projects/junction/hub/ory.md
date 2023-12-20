# ORY & Reseller Tutorial

[Ory](https://www.ory.sh/) is an identity and access management tool with
many products.

## Environments & Configuration

We have 3 main Ory projects which correspond to each environment we currently
have; Dev, Sandbox and Production. We use different URLs and API keys to manage
interactions with these projects. The `auth: grpc` service uses these values
to allow our Oauth client interactions to be authorised.
You can ask another developer or SRE for info on where to find these values.

Along with configuring ORY per environment, we also need to manage reseller's
per environment. You can find info on how this is done in the [Reseller
Configuration](https://engineering.snowfalltravel.com/docs/projects/junction/go/reseller-configuration)
page.

After creating necessary resellers and companies in mongo and consul, ORY
users can be assigned attributes to allow them to use Hub for actions their reseller
is allowed to. We assign these in ORY by using the `metadata_public` attribute.
This is only available to change through ORY's API

For example below rail providers are assigned to 'Rail Reseller',
meaning any user assigned to that reseller will receive rail content through
the booking flow search in Hub. Here is an example below of setting up a new
reseller.

## Reseller User Set Up

The first stages are to set up a company and reseller, however if this has already
been done you can skip to the ORY user.

### 1. Company

A company is a Junction PAY resource, which GO partially uses for logging quotations
and transactions made for bookings in the system. This needs creating, so we know
for a given reseller who to invoice. You can do this through the [Hub API: companies](https://engineering.snowfalltravel.com/docs/specifications/junction/hub/hub-api-spec#tag/companies)
endpoints or the Companies gRPC service. Once you have created the company, the ID will be
used in the reseller creation step.

### 2. Reseller

A reseller is a Junction GO resource, which we use for configuring clients who
wish to use the API, or have users associated with a reseller in a frontend (e.g Hub).
We can create this by using the [Hub API: resellers](https://engineering.snowfalltravel.com/docs/specifications/junction/hub/hub-api-spec#tag/resellers)
endpoints or the Resellers gRPC service. Important parts of the request
are:

#### Name and chosen providers attributes

```json
{
  "data": [
    {
      "type": "resellers",
      "attributes": {
        "name": "<reseller name>",
        "providers": [
          "<provider uuid>" // found in provider constants.py file
        ]
      }
    }
```
#### Company ID relationship

```json
"relationships": {
  "company": {
    "data": {
      "id": "<company_uuid>", // id from company creation step 1.
      "type": "companies"
    }
  }
}
```

#### Default currency relationship
```json
"relationships": {
  "currency": {
    "data": {
      "id": "<currency code>", // e.g. EUR, USD etc.
      "type": "currencies"
    }
  }
}
```

### 3. Consul

You should read over [Reseller Configuration](
https://engineering.snowfalltravel.com/docs/projects/junction/go/reseller-configuration)
to understand what we use the various fields for. However, the data set in the
previous step should align to consul Key/Value stores. In the future, we will
combine and automate this step and step 2 to promote this configuration having
created a reseller. For production, you will have to ask SRE to add this for you
currently.

In short the three pieces of config above require additions
in consul:

* `/providers/reseller-providers`
defines our providers which supply a given reseller.
```json
{
  "reseller_uuid": [
    "<provider_uuid>"
  ]
}
```
* `/client-api/reseller-currencies` defines our reseller's chosen default currency.
```json
{
  "<reseller_uuid>": "<currency_code>"
}
```
* `/client-api/reseller-pay-companies` references our reseller's company in PAY.
```json
{
  "<reseller_uuid>": "<company_uuid>"
}
```

### 4. ORY User

Ory user creation is the final step. You need a few pieces of info; `
reseller_id` if external reseller, the `role` for the user and the `email` of
the user. The preferred creation for internal users is to use the sign-up form,
which is currently related to each ORY environment. That allows the user to set
their own password, once they have confirmed this step we can update the user
using `PATCH` from [Ory's identity API](
https://www.ory.sh/docs/reference/api#tag/identity/operation/patchIdentity).

Depending on the use case of the reseller, their set-up may be different. (TBC)

The `POST` request from [Ory's identity API](
https://www.ory.sh/docs/reference/api#tag/identity/operation/createIdentity)
allows us to create users, there are some specific attribute sections we use.


* `traits` used to define the email address of the user
```json
"traits": {
    "email": "go-dev@snowfalltravel.com"
  }
```

* `schema` is used to define the version of the ORY schema we use.
This defines parameters in their account, e.g. login options.
```json
"schema_id": "string" // we have a default defined in ORY `a8bec...`.
```

* `metadata_public` is used to define the extra attributes which are custom to
our Ory usage, e.g. roles, reseller_id.

```json
{
  "reseller_id": "<reseller_uuid>", // if external reseller user
  "role": "reseller-admin" //role dependant
}
```

Our current roles with permissions are defined in the Monorepo
[here](https://git.snowfall.se/junction/junction/-/blob/main/python/snowfall/project/junction/hub/service/hub_api/permissions.py#L19)

