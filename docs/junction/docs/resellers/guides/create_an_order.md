---
title: Create an Order
sidebar_position: 1
---

# Create an Order Guide

This guide will outline the steps needed to create your first multi-modal order.

## Overview

This guide covers 7 steps in detail to get you to create your first order. By the end of this guide you should be familiar with the Reseller API and the key terminology here at Snowfall.

The steps to searching for an offer, selecting it, and creating an order go as follows:

1. Places - Prepare your list of origin and destinations
2. Trip Candidates - Search for offers
3. Trip Candidates - Retrieve offer results
4. Trip Candidates - Retrieve details of a specific offer
5. Quote - Select an offer
6. Quote - Retrieve all fare options for an offer
7. Order - Create an order

If you haven't already, please read the [**Key Concepts**](/docs/resellers/key-concepts/making_requests) section to familiarize yourself with API Requests.

---

## 1. Places - Prepare your list of Origin and Destinations

The Snowfall Reseller API connects any origin and destination, including cities, airports, train stations, bus stations, and ferry ports. To make this easier for our customers the API works best when using coordinates.

`GET /places endpoint`
<small><a href="/docs/resellers/openapi#tag/places" target="_blank">(view)</a></small>
provides a collection of place names, their place type, their coordinates, and other attributes.

Example:

```shell
curl -X GET 'https://api.junction.dev/places' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

The above endpoint should be stored for your implementation, using the pagination to get all the results.

### Query Parameter - limit

We can also limit the number of places returned with a **query parameter** `page[limit]` (default: `20`).

Example:

```shell
curl -X GET 'https://api.junction.dev/places?page[limit]=2' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

This will return **2** *places* in the response.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

```json
{
    "data": [
        {
            "id": "00014ab1-7b5d-5217-b956-daa1e0ac179c",
            "type": "places",
            "attributes": {
                "countryCode": "TH",
                "iataCode": null,
                "latitude": 18.7924876,
                "longitude": 98.9526159,
                "name": "Suthep",
                "timeZone": "Asia/Bangkok",
                "updatedAt": "2024-01-01T12:01:56Z"
            },
            "relationships": {
                "types": {
                    "data": [
                        {
                            "id": "city",
                            "type": "place-types"
                        }
                    ]
                }
            },
            "links": {
                "self": "https://api.junction.dev/places/00014ab1-7b5d-5217-b956-daa1e0ac179c"
            }
        },
        {
            "id": "00014b89-ad87-5b9d-ac7d-9beb69980259",
            "type": "places",
            "attributes": {
                "countryCode": "US",
                "iataCode": null,
                "latitude": 40.9468077,
                "longitude": -81.4670631,
                "name": "Green",
                "timeZone": "America/New_York",
                "updatedAt": "2023-11-15T15:56:20.253000Z"
            },
            "relationships": {
                "types": {
                    "data": [
                        {
                            "id": "city",
                            "type": "place-types"
                        }
                    ]
                }
            },
            "links": {
                "self": "https://api.junction.dev/places/00014b89-ad87-5b9d-ac7d-9beb69980259"
            }
        }
    ],
    "links": {
        "next": "https://api.junction.dev/places?page%5Bcursor%5D=MTogIjAwMDE0Yjg5LWFkODctNWI5ZC1hYzdkLTliZWI2OTk4MDI1OSIgMjogIjJkNmYyYTYxNGIzYTRkMWIiIDM6ICJlN2EwOTYyOWE3ZGVmNGUxIiA0OiAiYTJlNjM1NDliMjUwMzBkMiIgNTogIm51bGwi&page%5Blimit%5D=2"
    }
}
```

</details>

### Query Parameter - Pagination

Another query parameter `page[cursor]` can be used to skip to a page by specifying the id of the page (default: `""`).

After making a request and you receive a successful response, there will be a `links` attribute in the body.

```json
{
    "links": {
        "next": "https://api.junction.dev/places?page%5Bcursor%5D=MTogIjAwMDE0Yjg5LWFkODctNWI5ZC1hYzdkLTliZWI2OTk4MDI1OSIgMjogIjJkNmYyYTYxNGIzYTRkMWIiIDM6ICJlN2EwOTYyOWE3ZGVmNGUxIiA0OiAiYTJlNjM1NDliMjUwMzBkMiIgNTogIm51bGwi&page%5Blimit%5D=2"
    }
}
```

The value in `next` is the next page of your search. Simply, make a request again and apply this to the `page[cursor]` pagination query parameter.

Example:

```shell
curl -X GET --globoff 'https://api.junction.dev/places?page[limit]=2&page[cursor]=MTogIjAwMDE0Yjg5LWFkODctNWI5ZC1hYzdkLTliZWI2OTk4MDI1OSIgMjogIjJkNmYyYTYxNGIzYTRkMWIiIDM6ICJlN2EwOTYyOWE3ZGVmNGUxIiA0OiAiYTJlNjM1NDliMjUwMzBkMiIgNTogIm51bGwi' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

Please see [**API Specification**](/docs/resellers/openapi#tag/places/operation/get-places) for this endpoint for more information.

---

## 2. Trip Candidates - Search for offers

`POST /trip-candidates/searches`
<small><a href="/docs/resellers/openapi#tag/trips/operation/post-trip-candidates-searches" target="_blank">(view)</a></small>
initiates a search request for which Snowfall begins to search for offers that satisfy the trip.

Example:

```shell
curl -X POST 'https://api.junction.dev/trip-candidates/searches' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--data '<REQUEST_BODY>'
```

You will need to add a **Request Body** containing data:

:::important
The `sessionToken` used in the request body should be identical to the one used later in [(5) Offers](/docs/resellers/guides/create_an_order#5-quote---retrieve-all-fare-options-for-an-offer).

It is recommended to use 1 session token per user session.
:::

<details>
<summary>Expand (Request Body Example)</summary>

:::note
The `precision` (default: "area") attribute can be specified to search for either a `precise` location to the lat/lon co-ordinates **or** by a pre-defined radius using `area`.
:::


```json
{
  "data": {
    "type": "trip-candidate-searches",
    "attributes": {
      "sessionToken": "<SESSION_TOKEN>",
      "criteria": [
        {
          "origin": {
            "latitude": <PLACE_LATITUDE>,
            "longitude": <PLACE_LONGITUDE>,
            "precision": "precise",
          },
          "destination": {
            "latitude": <PLACE_LATITUDE>,
            "longitude": <PLACE_LONGITUDE>,
            "precision": "precise",
          },
          "departureAfter": "2024-01-03T12:00:42Z",  // Date/Time of departure
          "maximumConnections": 1
        }
      ],
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
            "id": "air",
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

As you can see we offer a variety of optional parameters that further specify the search. For example for a rail only search you would only declare the leg type `id="rail"` for the `allowedSegmentTypes` data object array.

<details>
<summary>Expand (allowedSegmentTypes Example)</summary>

```json
{
  "relationships": {
    "allowedSegmentTypes": {
      "data": [
        {
          "id": "rail",
          "type": "leg-types"
        }
      ]
    }
  }
}
```
</details>

We recommend you take these into consideration when designing your application, it will allow you to distinctly offer the user specific travel types or request multi-modal combinations.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

:::note
The `precision` (default: "area") attribute can be specified to search for either a `precise` location to the lat/lon co-ordinates **or** by a pre-defined radius using `area`.
:::

```json
{
    "data": {
        "id": "3e5da7b3-a487-455a-8706-d1b48004ddb7",
        "type": "trip-candidate-searches",
        "attributes": {
            "passengers": [
                {
                    "dateOfBirth": "1980-02-03"
                }
            ],
            "criteria": [
                {
                    "origin": {
                        "latitude": 37.9839412,
                        "longitude": 23.7283052,
                        "precision": "area"
                    },
                    "destination": {
                        "latitude": 40.9369224,
                        "longitude": 24.4122766,
                        "precision": "area"
                    },
                    "departureAfter": "2024-01-03T12:00:42Z",
                    "departureBefore": null,
                    "maximumConnections": 1
                }
            ],
            "expiresAt": "2024-01-01T12:45:56Z",
            "status": "pending"  // <-- Search is still pending
        },
        "links": {
            "self": "https://api.junction.dev/trip-candidates/searches/3e5da7b3-a487-455a-8706-d1b48004ddb7"
        }
    }
}
```
</details>

---

## 3. Trip Candidates - Retrieve offer results

`GET /trip-candidates/searches/{tripCandidateSearchid}`
<small><a href="/docs/resellers/openapi#tag/trips/operation/get-trip-candidates-searches-id" target="_blank">(view)</a></small>
is a polling endpoint for you to monitor the search requests status.

Example:

```shell
curl -X GET 'https://api.junction.dev/trip-candidates/searches/{tripCandidateSearchid}' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
```

The endpoint will return a `status: processing` until it has finished collecting results. Once it changes to "**completed**", you can stop polling the endpoint given that the results are ready. During the processing phase, you can receive results asynchronously.

##### Response Body Example:

<details>
<summary>Expand (Response Body Example)</summary>

:::note
The `precision` (default: "area") attribute can be specified to search for either a `precise` location to the lat/lon co-ordinates **or** by a pre-defined radius using `area`.
:::

```json
{
    "data": {
        "id": "3e5da7b3-a487-455a-8706-d1b48004ddb7",
        "type": "trip-candidate-searches",
        "attributes": {
            "passengers": [
                {
                    "dateOfBirth": "1980-02-03"
                }
            ],
            "criteria": [
                {
                    "origin": {
                        "latitude": 37.9839412,
                        "longitude": 23.7283052,
                        "precision": "area"
                    },
                    "destination": {
                        "latitude": 40.9369224,
                        "longitude": 24.4122766,
                        "precision": "area"
                    },
                    "departureAfter": "2024-01-03T08:10:22Z",
                    "departureBefore": null,
                    "maximumConnections": 1
                }
            ],
            "expiresAt": "2024-01-01T12:45:56Z",
            "status": "completed"  // <-- Search is now complete
        },
        "links": {
            "self": "https://api.junction.dev/trip-candidates/searches/3e5da7b3-a487-455a-8706-d1b48004ddb7"
        }
    }
}
```
</details>

---

## 4. Trip Candidates - Retrieve details for an offer

`GET /trip-candidates/searches/{tripCandidateSearchid}/offers`
<small><a href="/docs/resellers/openapi#tag/trips/operation/get-trip-candidates-searches-id-offers" target="_blank">(view)</a></small>
to receive the collection of offers that satisfy that trip, after the above `status` is "**completed**".

#### Query Parameter - include

We recommend you add the following query param to the request **includes=groups.options**:

Example:

```shell
curl -X GET 'https://api.junction.dev/trip-candidates/searches/{tripCandidateSearchid}/offers?include=groups.options' \
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
            "id": "b5231874-8f98-4eb7-9875-591aba73fef2",  // <-- Save this OfferId
            "type": "offers",
            "attributes": {
                "createdAt": "2024-01-01T12:00:02.057000Z",
                "expiresAt": "2024-01-01T12:45:56Z"
            },
            "relationships": {
                "groups": {
                    "data": [
                        {
                            "id": "05e5d23c-6636-50b0-8726-4d9d0a6d5cf7",  // <-- Save this OfferGroupId
                            "type": "offer-groups"
                        }
                    ]
                }
            },
            "links": {
                "self": "https://api.junction.dev/offers/b5231874-8f98-4eb7-9875-591aba73fef2"
            }
        },
    ],
    "links": {
        "next": "https://api.junction.dev/trip-candidates/searches/56a8b0e9-0e47-43f7-8fb8-5c8b532ea4a2/offers?page%5Bcursor%5D=MTogIjZjNjU4YTBiLThkOWYtNGEyYy04MGJjLWUzNTBkMDBmZjFjYyIgMjogImFmODIxM2M5NmE2N2NlZjciIDM6ICI1ODQ0MzU4YzIxMzFjMzBiIiA0OiAiYWRjNzA5NDA1YjFiYWFlNyIgNTogIntcIiRkYXRlXCI6IFwiMjAyMy0xMS0yN1QxMToxNzowMi42MTlaXCJ9Ig%3D%3D&page%5Blimit%5D=20"
    },
    "included": [
        {
            "id": "05e5d23c-6636-50b0-8726-4d9d0a6d5cf7",  // <-- Ensure is same OfferGroupId
            "type": "offer-groups",
            "attributes": {
                "expiresAt": "2024-01-01T12:45:56Z"
            },
            "relationships": {
                "options": {
                    "data": [
                        {
                            "id": "1af73627-58f4-5277-a58d-232a0aff6603",  // <-- Save this OfferOptionId
                            "type": "offer-options"
                        }
                    ]
                },
                "details": {
                    "data": [
                        {
                            "id": "311c2d02-5fcc-490b-8485-b3dc87131cbf",
                            "type": "trip-offer-group-details"
                        }
                    ]
                }
            },
            "links": {
                "self": "https://api.junction.dev/offers/groups/05e5d23c-6636-50b0-8726-4d9d0a6d5cf7"
            },
            "meta": {
                "providerId": "f9ce75d1-2025-4ab5-b5d7-69e4c14c053e"
            }
        },
    ]
}
```
</details>

---

## 5. Quote - Retrieve all fare options for an offer

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
The `sessionToken` used in the request body should be identical to the one used previously in [(2) Trip Candidate Search](/docs/resellers/guides/create_an_order#2-trip-candidates---search-for-offers).

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

## 6. Quote - Select an offer

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

## 7. Order - Create an order

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

2. Make sure (2) `POST /trip-candidates/searches` and (5) `POST /offers/quotes` have the same `sessionToken` in the request body!

3. Please contact us for more help!
