---
title: Python Example
sidebar_position: 1
---

# Python Example Usage of Reseller API

First we import some helpful modules, we use `json-api-doc` to flatten [json-api](https://jsonapi.org/) responses.
The `Content-Type` also has to be set to `application/vnd.api+json` for json-api compatibility.


```python
import sys
!{sys.executable} -m pip install --upgrade pip
!{sys.executable} -m pip install json-api-doc curlify

import requests
import json
import uuid
import time
import datetime
import json_api_doc
import curlify

s = requests.Session()
s.headers.update({
    'Content-Type': 'application/vnd.api+json',
})
```
Then we set the API key as bearer token.


```python
s.headers.update({
    'Authorization': 'Bearer <YOUR TOKEN>'
})
```

Then get all the places from `/places` and store them in a database, then create a query for certain places.
As an example we have hardcoded the following places:
- `36391863-ed79-5abd-9ed7-eede5677f843` London, UK
- `94b4b1e0-df99-574c-8727-d1dcad2fad14` Amsterdam, The Netherlands

### /places - Using coordinates directly

Alternatively you can also use coordinates directly without using our collection of places.

```python
london = json_api_doc.deserialize(s.get("https://api.sandbox.junction.dev/places/36391863-ed79-5abd-9ed7-eede5677f843").json())
amsterdam = json_api_doc.deserialize(s.get("https://api.sandbox.junction.dev/places/94b4b1e0-df99-574c-8727-d1dcad2fad14").json())
```

Next generate a session token to be used in future requests for the same booking flow.


```python
session_token = uuid.uuid4().hex
```

Now we can search for trips and offers for the trips by creating a trip-canidates search.


```python
tomorrow = f"{(datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()}Z"

trip_candidate_search = json_api_doc.deserialize(s.post(
    "https://api.sandbox.junction.dev/trip-candidates/searches",
    data=json.dumps({
      "data": {
        "type": "trip-candidate-searches",
        "attributes": {
          "sessionToken": session_token,
          "passengers": [
            {
              "dateOfBirth": "1980-02-03"
            }
          ],
          "criteria": [
            {
              "origin": {
                "latitude": london["latitude"],
                "longitude": london["longitude"]
              },
              "destination": {
                "latitude": amsterdam["latitude"],
                "longitude": amsterdam["longitude"],
              },
              "departureAfter": tomorrow,
              "maximumConnections": 1
            }
          ]
        },
        "relationships": {
          "allowedSegmentTypes": {
            "data": [
              {
                "id": "air",
                "type": "leg-types"
              },
              {
                "id": "rail",
                "type": "leg-types"
              },
              {
                "id": "bus",
                "type": "leg-types"
              },
              {
                "id": "ferry",
                "type": "leg-types"
              }
            ]
          }
        }
      }
    })
).json())
```

Next we can retrieve offers for the trip, it can take a few seconds for the offers to be populated.


```python
time.sleep(5) # Wait for offers.
offers = json_api_doc.deserialize(s.get(
    f"https://api.sandbox.junction.dev/trip-candidates/searches/{trip_candidate_search['id']}/offers?include=groups,groups.options.details"
).json())
```
<details>
<summary>Trip offer results</summary>

  ```python
    [
      {
        "id": "185a5c1b-f800-40c8-a307-825ca8ed900d",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "8bcaa409-63ae-5bac-95d0-9ecb2c3249e2",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.307000Z",
            "options": [
              {
                "id": "a9739aa7-9a12-5923-8523-9038480b4d52",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "30.78"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "30.78"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "0dc1403f-24ea-4ad8-acb5-7383715d6d3b",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "0a16492d-4f49-4d3f-845b-71db088907c9",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "0a16492d-4f49-4d3f-845b-71db088907c9",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "44b58864-66cd-4eba-9c81-b47f5c110b83",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "987efc99-14a9-53cc-b0ab-b6ab9d2e3990",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.422000Z",
            "options": [
              {
                "id": "6dab20cd-4db9-58fe-82ca-b8d8b9c90324",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "38.07"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "38.07"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "e099f201-3cf3-4403-8a36-de2f5aa48359",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "2d54da68-c1e5-4809-99e9-42d66f676ca3",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "2d54da68-c1e5-4809-99e9-42d66f676ca3",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "4f82a2e1-ff68-42d1-99dc-d8eb7a33d734",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30.001000Z",
        "groups": [
          {
            "id": "33426cf0-a093-5c39-ad86-684da5c80637",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.075000Z",
            "options": [
              {
                "id": "2a7d843b-3e1c-5c1e-ba63-54e7cc0b0a36",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "8.10"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "8.10"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "a0854261-61db-40e6-a218-124240352b5a",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "45537f1a-ba15-48ab-803c-2b528e318d15",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "45537f1a-ba15-48ab-803c-2b528e318d15",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "6158afc4-e9cf-49c5-baa1-cbc2fa456647",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "75664976-b772-5122-898c-b3b72ca726a8",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.399000Z",
            "options": [
              {
                "id": "0d2b0377-d83e-553e-84ba-37d5a6fc87dd",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "63.18"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "63.18"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "7efc7e87-8115-49e2-a5bb-30342019383e",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "8034c7c9-099a-4be7-907a-af51f2e8e13f",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "8034c7c9-099a-4be7-907a-af51f2e8e13f",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "620889b4-dabe-4bcc-8422-14291cf6fcf4",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "04530f90-cac7-5563-b86f-0ff4c34beddc",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.134000Z",
            "options": [
              {
                "id": "31df88cc-e467-5cae-88fb-72ab5ca304d9",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "29.16"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "29.16"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "45cd8126-26f2-4606-8945-b41fc1beba5c",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "e8b332e1-6769-49fd-abba-b0729b354085",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "e8b332e1-6769-49fd-abba-b0729b354085",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "64ade104-8341-47da-a3ce-51bfbad876e1",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "6e453b93-4ab0-5169-8e8d-3c0d36d4316e",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.251000Z",
            "options": [
              {
                "id": "2307ce0b-2341-5d2b-b0a0-be3ca738c96a",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "42.12"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "42.12"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "6eb38c82-b50a-46ce-8fe3-951fb7d94dcb",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "5d98eb3c-2197-46c4-a4e1-5ca1c9cae22e",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "5d98eb3c-2197-46c4-a4e1-5ca1c9cae22e",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "780f1f79-3c59-498a-b982-94c564f5af88",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "ec57e744-23c4-55ad-a39f-4ba5b5f0c989",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.371000Z",
            "options": [
              {
                "id": "7d1cd125-a194-5252-814b-fc7928468188",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "79.38"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "79.38"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "ab09b46b-8323-449c-bc7c-b4e43339d33c",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "a8fe7d91-e907-47c8-b767-f5e5f6b48369",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "a8fe7d91-e907-47c8-b767-f5e5f6b48369",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "7863cb8c-0d37-4b8f-8ce7-6b94ae56bf64",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "0b98d851-4e53-5330-bc71-bd2894b4a9ec",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.283000Z",
            "options": [
              {
                "id": "217b333c-b840-57f9-b278-7c725b221a32",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "19.44"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "19.44"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "8945ef1a-4af4-4f53-8549-273cc3857b05",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "82b5a2eb-c4e0-432c-a243-d5292c2eda07",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "82b5a2eb-c4e0-432c-a243-d5292c2eda07",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "879767a8-7ed1-49c3-be5c-50a767bb3939",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "f7757b3e-c238-5acb-a31a-59fba3b818d5",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.464000Z",
            "options": [
              {
                "id": "58045b49-dd62-5a00-91c8-12b606d6f6ca",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "34.83"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "34.83"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "18ff945d-2275-4f27-81d9-b44a1826a99b",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "4b64f3c3-13e8-4889-a849-0ac57714794c",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "4b64f3c3-13e8-4889-a849-0ac57714794c",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "a210d7be-460b-4592-9eb4-21a8c1735a33",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "ee6f9721-6c67-5389-9afe-c83b83685cba",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.217000Z",
            "options": [
              {
                "id": "51374e18-e0ce-52fd-850a-cc9ae76ba789",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "46.98"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "46.98"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "55fb7a96-61f9-4da5-a572-4d934446cc02",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "0ad5692b-f44b-40c2-addc-8ca7dcf7ec0c",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "0ad5692b-f44b-40c2-addc-8ca7dcf7ec0c",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "ac4cad96-6c21-4249-8a5d-bbe632c694ba",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "ff438345-b1f0-5562-a9e3-97bb07d736df",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.098000Z",
            "options": [
              {
                "id": "8ba7a374-1457-5dd4-9fa1-b22989fff190",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "31.59"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "31.59"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "2b8ed04b-d9c5-4532-86ce-b5ceaac683eb",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "85e7211c-fc6b-4989-9f10-fe762a486b61",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "85e7211c-fc6b-4989-9f10-fe762a486b61",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "cc3d2e5d-56da-4f0c-9a1b-2c7093f8c119",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30.001000Z",
        "groups": [
          {
            "id": "549b87a7-29ea-58a3-a803-9d57269fceef",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.443000Z",
            "options": [
              {
                "id": "25eb5191-41c4-5f74-b4a0-654d53bfc3ba",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "57.51"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "57.51"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "499a27db-af6c-4b7d-b171-d35f05d03929",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "dcc05186-5931-4417-8d79-215a77672649",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "dcc05186-5931-4417-8d79-215a77672649",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "ce57918f-a6de-44d6-825a-e42bcce7b101",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "f33505a3-b9e4-521c-8c91-0dcaf110a72d",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.350000Z",
            "options": [
              {
                "id": "735a18d2-e526-5669-a3c0-c3f41da43077",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "18.63"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "18.63"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "ccf6cc61-6cb7-4650-bf4c-a7b9d5473375",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "87f425a1-eacc-4802-ae5a-a3e49b142fcb",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "87f425a1-eacc-4802-ae5a-a3e49b142fcb",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "e52a9d31-59bb-4cbd-abfc-11b048bfe07b",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "24f0ecf7-e4f9-5717-8ed9-f3e53261fa26",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.165000Z",
            "options": [
              {
                "id": "f926f7e4-be82-5a7c-bc54-ffd2158e43f0",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "27.54"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "27.54"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "8f258d46-b49c-442f-af18-9ca59c28b229",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "d4ede210-353d-4be1-a844-9f8ca3fe6a62",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "d4ede210-353d-4be1-a844-9f8ca3fe6a62",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "ec4887cc-c231-406b-b864-08fb94a229bd",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "c6d4ec7b-7bc7-51a7-bb00-867f2f92ad36",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.194000Z",
            "options": [
              {
                "id": "19d8c82d-2c17-5534-80e2-4331e8a319ad",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "27.54"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "27.54"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "afc06c3d-e63c-41d9-9b5b-8f0ef9b9cade",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "7a1245fa-96e0-4dd0-ba96-641e83e624cb",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "7a1245fa-96e0-4dd0-ba96-641e83e624cb",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "edd25172-c633-4dce-8851-6c1dc92c22bd",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "553a8f5c-eca5-55ee-8f52-60ebc0890898",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.484000Z",
            "options": [
              {
                "id": "b823922c-e963-5b8d-8ff6-3765bd5435cf",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "27.54"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "27.54"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "3d753715-b561-452a-ae7c-a72c0440cfe1",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "956dd51a-d316-442f-84ed-5ce2baf077af",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "956dd51a-d316-442f-84ed-5ce2baf077af",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      },
      {
        "id": "eeb73b94-ab4e-41b0-9f21-efd7d16d784a",
        "type": "offers",
        "expiresAt": "2023-08-28T12:33:30Z",
        "groups": [
          {
            "id": "f134b3a5-9950-54a3-a117-07de5524359c",
            "type": "offer-groups",
            "expiresAt": "2023-08-28T12:33:30.329000Z",
            "options": [
              {
                "id": "bc0036f7-e3d4-5be9-b8ca-9919acc80329",
                "type": "offer-options",
                "price": {
                  "currency": "GBP",
                  "amount": "40.50"
                },
                "priceBreakdown": [
                  {
                    "price": {
                      "currency": "GBP",
                      "amount": "40.50"
                    },
                    "breakdownType": "base-fare"
                  }
                ],
                "brandName": "BASIC",
                "baggageAllowances": [],
                "details": [
                  {
                    "id": "106c3ab5-6bbc-4392-b2da-8925b546373a",
                    "type": "trip-offer-option-details",
                    "cabinClassName": "Economy",
                    "baggageAllowances": [],
                    "amenities": {
                      "beverage": {
                        "availability": "unspecified"
                      },
                      "entertainment": {
                        "availability": "unspecified"
                      },
                      "food": {
                        "availability": "unspecified"
                      },
                      "power": {
                        "availability": "unspecified"
                      },
                      "wifi": {
                        "availability": "unspecified"
                      }
                    },
                    "details": {
                      "id": "51ad43f2-1838-48fa-8b43-a2934bedb335",
                      "type": "trip-offer-group-details"
                    },
                    "cabinClass": {
                      "id": "economy",
                      "type": "cabin-classes"
                    }
                  }
                ]
              }
            ],
            "details": [
              {
                "id": "51ad43f2-1838-48fa-8b43-a2934bedb335",
                "type": "trip-offer-group-details"
              }
            ]
          }
        ]
      }
    ]
  ```
</details>
Offer quotes can be used to retrieve the final price.
If the offer that you got contains multiple groups, quote creation should contain option IDs per each offer group, not only for one, otherwise order creation will fail.


```python
quotes = json_api_doc.deserialize(s.post(
    "https://api.sandbox.junction.dev/offers/quotes",
    data=json.dumps({
      "data": {
        "type": "trip-offer-price-quotes",
        "attributes": {
          "sessionToken": session_token
        },
        "relationships": {
          "offer": {
            "data": {
              "id": offers[0]["id"],
              "type": "offers"
            }
          },
          "options": {
            "data": [
              {
                "id": offers[0]["groups"][0]["options"][0]["id"],
                "type": "offer-options"
              }
            ]
          }
        }
      }
    })
).json())
```
<details>
<summary>Offer quote results</summary>

  ```
    {
      "id": "cab4644b-eb9c-4545-af52-d96568f84d22",
      "type": "trip-offer-price-quotes",
      "expiresAt": "2023-08-28T12:03:35.812585Z",
      "price": null,
      "priceBreakdown": [],
      "penalties": [],
      "required": [],
      "rules": [],
      "status": "pending",
      "offer": {
        "id": "185a5c1b-f800-40c8-a307-825ca8ed900d",
        "type": "offers"
      },
      "options": [
        {
          "id": "a9739aa7-9a12-5923-8523-9038480b4d52",
          "type": "offer-options"
        }
      ]
    }
  ```
</details>


Finally you can create a booking through a `POST` request to `/orders` with the price quote id.

```python
order = json_api_doc.deserialize(s.post(
    "https://api.sandbox.junction.dev/orders",
    data=json.dumps({
      "data": {
        "type": "orders",
        "attributes": {
          "contactDetails": {
            "email": "john.smith@example.com",
            "address": {
              "addressLines": [
                "Street name 7"
              ],
              "countryCode": "GB",
              "postalCode": "12345",
              "city": "London"
            },
            "phoneNumber": "+37069248392"
          },
          "passengers": [
            {
              "firstName": "John",
              "lastName": "Smith",
              "title": "mr",
              "gender": "male",
              "dateOfBirth": "1980-02-03",
              "travelerDocument": {
                "documentType": "passport",
                "documentNumber": "1543343434",
                "documentIssueCountry": "GB",
                "documentExpirationDate": "2025-02-03",
                "documentIssueDate": "2025-02-03",
                "nationality": "ES",
                "residenceCountryCode": "NL"
              }
            }
          ],
          "residenceAddress": {
            "addressLines": [
              "Street name 7"
            ],
            "countryCode": "GB",
            "postalCode": "12345",
            "city": "London"
          }
        },
        "relationships": {
          "quote": {
            "data": {
              "id": quotes["id"],
              "type": "trip-offer-price-quotes"
            }
          }
        }
      }
    })
).json())
```
