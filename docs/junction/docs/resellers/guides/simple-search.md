---
title: Perform Simple Search
sidebar_position: 1
---

# Perform a Simple Search Guide

This guide will outline the steps needed to create your simple search with an example for a taxi trip.

## Overview

This guide covers 5 steps in detail to get you to search a trip and create an order.

1. Initiate simple offer search for a trip
2. Poll search status
3. Retrieve offers
4. Quote - Retrieve all fare options for an offer
5. Quote - Poll quote status
6. Create an order for selected offer

If you haven't already, please read the [**Key Concepts**](/docs/resellers/key-concepts/making-requests) section to familiarize yourself with API Requests.

---

## 1. Initiate simple offer search for a trip

Simple search API allows to easily search by providing geographical coordinates of origin and destination of the trip.

`POST /simple-offers/searches`
<small><a href="/docs/resellers/openapi#tag/offers/operation/post-simple-offers-searches" target="_blank">(view)</a></small>
endpoint initiates a search request for which Snowfall begins to search for offers that satisfy the trip.

Example:

```shell
curl -X POST 'https://api.junction.dev/simple-offers/searches' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--data '<REQUEST_BODY>'
```

You will need to add a Request Body containing data:

:::important
The `sessionToken` used in the request body should be identical to the one used later in [(5) Quotes](/docs/resellers/guides/simple-search#4-quote---retrieve-all-fare-options-for-an-offer).

It is recommended to use 1 session token per user session.
:::


<details>
<summary>Expand (Request Body Example)</summary>

```json
{
  "data": {
    "type": "simple-offer-searches",
    "attributes": {
      "sessionToken": "<SESSION_TOKEN>",
      "criteria": {
        "origin": {
            "latitude": <PLACE_LATITUDE>,
            "longitude": <PLACE_LONGITUDE>
        },
        "destination": {
            "latitude": <PLACE_LATITUDE>,
            "longitude": <PLACE_LONGITUDE>
        },
        "departureAfter": "2021-02-03:00:00Z"  // Date/Time of departure
      },
      "passengers": [
        {
          "dateOfBirth": "1980-02-03"
        }
      ]
    },
    "relationships": {
      "allowedSegmentTypes": {
        "data": [
          {
            "id": "taxi",
            "type": "leg-types"
          }
        ]
      }
    }
  }
}
```
</details>


To make a search request you need to input *origin*, *destination*, *dates*, and passengers *date of birth*.

As you can see we offer a variety of optional parameters that further specify the search. For example for a taxi only search you would only declare the leg type `id="taxi"` for the `allowedSegmentTypes` data object array.

<details>
<summary>Expand (allowedSegmentTypes Example)</summary>

```json
{
  "relationships": {
    "allowedSegmentTypes": {
      "data": [
        {
          "id": "taxi",
          "type": "leg-types"
        }
      ]
    }
  }
}
```
</details>

We recommend you take these into consideration when designing your application, it will allow you to distinctly offer the user specific travel types or request multi-modal combinations.

:::note
In case of `taxi` offers will cover the entire trip, as currently multi-modality is not supported for `taxi` segments.
:::

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": {
        "id": "7a656c90-3ada-4869-94e3-34ce04dc26d7",
        "type": "simple-offer-searches",
        "attributes": {
            "passengers": [
                {
                    "dateOfBirth": "1980-02-03"
                }
            ],
            "criteria": {
                "origin": {
                    "latitude": 50.8356748,
                    "longitude": 4.3362419
                },
                "destination": {
                    "latitude": 51.19763610627596,
                    "longitude": 3.2177298798723357
                },
                "departureAfter": "2021-02-03T08:00:00Z"
            },
            "expiresAt": "2021-02-03T10:13:02.504088Z",
            "status": "pending"  // <-- Search is still pending
        },
        "links": {
            "self": "https://api.junction.dev/offers/searches/7a656c90-3ada-4869-94e3-34ce04dc26d7"
        }
    }
}
```
</details>

---

## 2. Poll search status

`GET /offers/searches/{offerSearchId}`
<small><a href="/docs/resellers/openapi#tag/offers/operation/get-offers-searches-id" target="_blank">(view)</a></small>
is a polling endpoint for you to monitor the search requests status.

Example:

```shell
curl -X GET 'https://api.junction.dev/offers/searches/{offerSearchId}' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
```

The endpoint will return a `status: processing` until it has finished collecting results. Once it changes to "**completed**", you can stop polling the endpoint given that the results are ready. During the processing phase, you can receive results asynchronously.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": {
        "id": "c2474ce4-8309-4a90-b431-21f780336b10",
        "type": "trip-offer-searches",
        "attributes": {
            "expiresAt": "2023-12-21T12:21:19.964000Z",
            "passengers": [
                {
                    "dateOfBirth": "1980-02-03"
                }
            ],
            "status": "completed"  // <-- Search is now complete
        },
        "relationships": {
            "offers": {
                "data": []
            }
        },
        "links": {
            "self": "https://api.junction.dev/offers/searches/c2474ce4-8309-4a90-b431-21f780336b10"
        }
    }
}
```
</details>

---

## 3. Retrieve offers

`GET /offers/searches/{offerSearchId}/offers`
<small><a href="/docs/resellers/openapi#tag/offers/operation/get-offers-searches-id-offers" target="_blank">(view)</a></small>
to receive the collection of offers that satisfy that trip, after the above `status` is "**completed**".

#### Query Parameter - include

We recommend you add the following query param to the request **includes=groups.options**:

Example:

```shell
curl -X GET 'https://api.junction.dev/offers/searches/{offerSearchId}/offers?include=groups.options' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
```

Each of the returned offers includes a list of `Offer Group id` which encompass one or multiple segments. For example a trip that includes a flight segment and a rail segment would have 1 offer group for the flight portion, and 1 offer group for the rail portion.

Furthermore, each offer group includes a list of `Offer Option id`  that represent the distinct fares and price points available for that offer group. For example: a rail offer group can include a economy offer option priced at £30 and a premium offer option priced at £45.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
  "data": [
    {
      "id": "069d56d4-f713-4434-89ed-e664d74765fa",
      "type": "offers",
      "attributes": {
        "createdAt": "2023-12-21T12:38:48.263000Z",
        "expiresAt": "2023-12-21T12:51:22.001000Z"
      },
      "relationships": {
        "groups": {
          "data": [
            {
              "id": "b6023669-b700-5399-82d4-c6657753b912",
              "type": "offer-groups"
            }
          ]
        }
      },
      "links": {
        "self": "https://api.junction.dev/offers/069d56d4-f713-4434-89ed-e664d74765fa"
      }
    }
  ],
  "included": [
    {
      "id": "b6023669-b700-5399-82d4-c6657753b912",
      "type": "offer-groups",
      "attributes": {
        "expiresAt": "2023-12-21T12:51:22.117000Z"
      },
      "relationships": {
        "options": {
          "data": [
            {
              "id": "9f2a31af-ab94-521b-82e2-3fd01fbf2b21",
              "type": "offer-options"
            }
          ]
        },
        "details": {
          "data": [
            {
              "id": "7fb38ebe-9c64-43d8-a1bd-cf78ac875bab",
              "type": "trip-offer-group-details"
            }
          ]
        }
      },
      "links": {
        "self": "https://api.junction.dev/offers/groups/b6023669-b700-5399-82d4-c6657753b912"
      },
      "meta": {
        "providerId": "7b13cd40-464d-41fc-a71d-f5c63f9817d3"
      }
    },
    {
      "id": "9f2a31af-ab94-521b-82e2-3fd01fbf2b21",
      "type": "offer-options",
      "attributes": {
        "price": {
          "currency": "SEK",
          "amount": "224.26"
        },
        "priceBreakdown": [
          {
            "price": {
              "currency": "SEK",
              "amount": "212.77"
            },
            "breakdownType": "base-fare"
          },
          {
            "price": {
              "currency": "SEK",
              "amount": "11.49"
            },
            "breakdownType": "service-mark-up"
          }
        ],
        "brandName": "Fixed",
        "baggageAllowances": []
      },
      "relationships": {
        "details": {
          "data": [
            {
              "id": "5df8da77-dc4b-433e-97f0-5bcc12703648",
              "type": "trip-offer-option-details"
            }
          ]
        }
      },
      "links": {
        "self": "https://api.junction.dev/offers/options/9f2a31af-ab94-521b-82e2-3fd01fbf2b21"
      }
    }
  ]
}
```
</details>

---

## 4. Quote - Retrieve all fare options for an offer

`POST /offers/quotes`
<small><a href="/docs/resellers/openapi#tag/trips/operation/post-offers-quotes" target="_blank">(view)</a></small>
is used to get the most up to date price and details for an offer selected.

The `OFFER_ID` and `OFFER_OPTION_ID` you selected in the previous endpoint are used in the request body.

Example:

```shell
curl -X POST 'https://api.junction.dev/offers/quotes' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--data '<REQUEST_BODY>'
```

You will need to add a **Request Body** containing data:

<details>
<summary>Expand (Request Body Example)</summary>

```json
{
    "data": {
        "type": "trip-offer-price-quotes",
        "attributes": {
            "sessionToken": "<SESSION_TOKEN>"
        },
        "relationships": {
            "offer": {
                "data": {
                    "id": "<OfferId>",
                    "type": "offers"
                }
            },
            "options": {
                "data": [
                    {
                        "id": "<OfferOptionId>",
                        "type": "offer-options"
                    }
                ]
            }
        }
    }
}
```
</details>

:::important
The `sessionToken` used in the request body should be identical to the one used previously in [(1) Initiate simple offer search for a trip](/docs/resellers/guides/simple-search#1-initiate-simple-offer-search-for-a-trip).

It is recommended to use 1 session token per user session.
:::

The response returns a single `Offer Price Quote ID` for every offer.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": {
        "id": "896045d3-a218-4c76-bdf5-a7c88f92e473",  // <-- Offer Price Quote Id
        "type": "trip-offer-price-quotes",
        "attributes": {
            "expiresAt": "2024-01-01T12:45:56Z",
            "price": null,
            "priceBreakdown": [],
            "penalties": [],
            "required": [],
            "rules": [],
            "status": "pending"
        },
        "relationships": {
            "offer": {
                "data": {
                    "id": "2fceccb3-ca73-4958-9dcc-f33fe9dd0176",
                    "type": "offers"
                }
            },
            "options": {
                "data": [
                    {
                        "id": "6d494b26-4ea8-5560-b15c-a0873c4b535f",
                        "type": "offer-options"
                    }
                ]
            }
        },
        "links": {
            "self": "https://api.junction.dev/offers/quotes/896045d3-a218-4c76-bdf5-a7c88f92e473"
        }
    }
}
```
</details>

---

## 5. Quote - Poll quote status

`GET /offers/quotes/{OfferPriceQuoteId}`
<small><a href="/docs/resellers/openapi#tag/trips/operation/get-offers-quotes-id" target="_blank">(view)</a></small>
is a polling endpoint for you to monitor the quote requests status.

The `OfferPriceQuoteId` is the chosen offer from the response above.

Example:

```shell
curl -x GET 'https://api.junction.dev/offers/quotes/<OfferPriceQuoteId>' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

The endpoint will return a `status: processing` until it has finished collecting results. Once it changes to "**completed**", you can stop polling the endpoint given that the results are ready.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": {
        "id": "896045d3-a218-4c76-bdf5-a7c88f92e473",
        "type": "trip-offer-price-quotes",
        "attributes": {
            "expiresAt": "2024-01-01T12:45:56Z",
            "price": {
                "currency": "EUR",
                "amount": "43.31"
            },
            "priceBreakdown": [
                {
                    "price": {
                        "currency": "EUR",
                        "amount": "43.31"
                    },
                    "breakdownType": "base-fare"
                },
                {
                    "price": {
                        "currency": "EUR",
                        "amount": "0.31"
                    },
                    "breakdownType": "service-mark-up"
                }
            ],
            "penalties": [],
            "required": [],
            "rules": [
                {
                    "title": "FAKE FARE RULE",
                    "body": "THIS PRICE QUOTE IS NOT GENUINE. IT ORIGINATES FROM THE MOCK PROVIDER"
                }
            ],
            "status": "completed"
        },
        "relationships": {
            "offer": {
                "data": {
                    "id": "2fceccb3-ca73-4958-9dcc-f33fe9dd0176",
                    "type": "offers"
                }
            },
            "options": {
                "data": [
                    {
                        "id": "6d494b26-4ea8-5560-b15c-a0873c4b535f",
                        "type": "offer-options"
                    }
                ]
            }
        },
        "links": {
            "self": "https://api.junction.dev/offers/quotes/896045d3-a218-4c76-bdf5-a7c88f92e473"
        }
    }
}
```
</details>

---

## 6. Order - Create an order

`POST /orders`
<small><a href="/docs/resellers/openapi#tag/trips/operation/post-orders" target="_blank">(view)</a></small>
endpoint is used to create the order.

A request body is required which will contain the `OFFER_ID`, the `OFFER_OPTION_ID`, and the `OfferPriceQuoteId` saved from before.

Example:

```shell
curl -X POST 'https://api.junction.dev/orders' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--data-raw '<YOUR_DATA>'
```

You will need to add a **Request Body** containing data:

<details>
<summary>Expand (Request Body Example)</summary>

```json
{
    "data": {
        "type": "orders",
        "attributes": {
            "passengers": [
                {
                    "firstName": "JohnA",
                    "lastName": "SmithB",
                    "title": "mr",
                    "gender": "male",
                    "dateOfBirth": "1990-02-04",
                    "travelerDocument": {
                        "nationality": "GB"
                    }
                }
            ],
            "contactDetails": {
                "email": "john.smith+a@example.com",
                "address": {
                    "addressLines": [
                        "Street name 7"
                    ],
                    "countryCode": "GB",
                    "postalCode": "12346",
                    "city": "London"
                },
                "phoneNumber": "+306951234568"
            }
        },
        "relationships": {
            "offer": {
                "data": {
                    "id": "<OfferId>",
                    "type": "offers"
                }
            },
            "options": {
                "data": [
                    {
                        "id": "<OfferOptionId>",
                        "type": "offer-options"
                    }
                ]
            },
            "quote": {
                "data": {
                    "id": "<OfferPriceQuoteId>",
                    "type": "trip-offer-price-quotes"
                }
            }
        }
    }
}
```

</details>

Your order should now be complete.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": {
        "id": "45d227f5-1db4-4365-9bc6-d232d47b3355",
        "type": "orders",
        "attributes": {
            "createdAt": "2024-01-01T12:45:56Z",
            "passengers": [
                {
                    "firstName": "JohnA",
                    "dateOfBirth": "1990-02-04",
                    "title": "mr",
                    "lastName": "SmithB",
                    "gender": "male"
                }
            ]
        },
        "relationships": {
            "journey": {
                "data": {
                    "id": "b6ef672b-bce4-4f95-b84d-fe2a5fb8d1b2",
                    "type": "journeys"
                }
            },
            "bookings": {
                "data": [
                    {
                        "id": "7abe7d66-fc43-4fd5-b149-61a77167a11e",
                        "type": "trip-bookings"
                    }
                ]
            }
        },
        "links": {
            "self": "https://api.junction.dev/orders/45d227f5-1db4-4365-9bc6-d232d47b3355"
        }
    }
}
```
</details>

---

## Need help?

1. Make sure your access tokens are always added to the request headers

2. Make sure (1) `POST /simple-offers/searches` and (4) `POST /offers/quotes` have the same `sessionToken` in the request body!

3. Please contact us for more help!
