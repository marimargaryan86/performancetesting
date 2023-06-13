# Reseller Configuration

## What we mean by configuration

Configuration refers to values set in **Key/Values** in [Consul](https://www.consul.io/)

We use Consul due to its integration with Nomad. A Consul Key/Value is passed to
our services just like any other environment variable. When a Consul value gets
updated, the service _should_ update automatically, if the `change_mode = "restart"`
`template` entry is set.

SRE are the only team with `production` Consul access, however, all developers
should be able to use: [https://consul.junction.dev](https://consul.junction.dev),
if you find you cannot access this contact SRE.

## What is a Reseller

A reseller is the consumer of our **publicly** facing services, a great example would
be [res.se](https://res.se).

A reseller will ultimately consume different content from our offerings and want
to customise this content in potentially several ways.

## What is currently configured

At a high level, there are three 'options' for a reseller to configure, there is
one other configurable value but this is not an option to the reseller.

The three options are:

* [`RESELLER_CURRENCIES`](#reseller-currencies) - Currency used in all interactions
* [`RESELLER_PROVIDERS`](#reseller-providers) - Providers that are used to return
content
* [`RESELLER_DISABLED_OPERATORS`](#reseller-disabled-operators) - Operators to
not return within a given providers content

The configurable that needs to be set, but not on the request of a reseller is:
[`RESELLER_PAY_COMPANIES`](#reseller-pay-companies)

### Reseller Currencies

#### Consul Key

`"${var.environment}/client-api/reseller-currencies"`

#### Structure

```json
{
  "{RESELLER_ID}": "{CURRENCY_CODE}",
  "reseller-id-2": "USD",
  ...
}
```

#### Effect

Reseller Currencies is set at a `client-api` level. When a request is received
from an authenticated user belonging to the reseller, the currency code they have
configured is retrieved and passed onto any services downstream. Currently, this
affects the currencies of returned offers, price quotes, and the currency bookings
are paid in.

### Reseller Providers

#### Consul Key

`"${var.environment}/providers/reseller-providers"`

#### Structure

```json
{
  "{RESELLER_ID}": ["{PROVIDER_NAME}", "{PROVIDER_NAME}"],
  "reseller-id-2": ["ba-ndc", "duffel", ...],
  ...
}
```

#### Effect

Reseller Providers is set across all providers, upon receiving an offer search
each provider will determine, based on the `reseller_id`, whether it should continue
to process the request. This effectively 'filters' providers out of results a reseller
receives and can use further into the booking process.

### Reseller Disabled Operators

#### Consul Key

`"${var.environment}/providers/reseller-disabled-operators"`

#### Structure

```json
{
  "{RESELLER_ID}": {
    "{PROVIDER_NAME}": ["{OPERATOR_ID}", "{OPERATOR_ID}", ...],
    ...
  },
  "reseller-id-2": {
    "duffel": ["ba"]
  },
  ...
}
```

#### Effect

Reseller Disabled Operators is set in the offers service, upon import of an offer,
the service determines if the operator/vendor of any segments in the offer contain
the ID of a disabled operator for that provider. If it finds a match, it dismisses
the import of the offer.

A good example of the reason for this configurable is to only have an operator be
returned from Provider A, rather than B and C also, if the rates with A are more
favourable.

### Reseller Pay Companies

#### Consul Key

`"${var.environment}/client-api/reseller-pay-companies"`

#### Structure

```json
{
  "{RESELLER_ID}": "{PAY_COMPANY_ID}",
  "reseller-id-2": "07e29239-2740-4bf5-ae0f-004d864e3a40",
  ...
}
```

#### Effect

Reseller PAY Companies is used to track the related Company resource in PAY, that
represents a Reseller. This is then used to track charges to the reseller for
conversions, transactions, etc.

Eventually, this is likely to be redundant (a PAY Company ID **will** be
the reseller ID, or perhaps a new Reseller resource will be created).
