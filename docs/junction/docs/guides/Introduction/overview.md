---
title: Overview
sidebar_position: 2
---

# Overview

We will be making a single API request to confirm we have access!

Before starting you should already have:
1. **Access token**
2. Our [**key terms guide**](/docs/resellers/key-concepts/making-requests) at hand

## Sending your first API request

The Snowfall Reseller API connects any origin and destination, including cities, airports, train stations, bus stations, and ferry ports.

`GET /places/types` [(view)](/docs/resellers/openapi#tag/places/operation/get-places-types)  provides a collection of place types.

##### Let's try it:

```shell
curl -X GET 'https://api.sandbox.junction.dev/places/types' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

You should receive a response something similar to this:

```json
{
    "data": [
        {
            "id": "airport",
            "type": "place-types",
            "attributes": {
                "name": "airport"
            },
            "links": {
                "self": "https://api.sandbox.junction.dev/places/types/airport"
            }
        },
    ],
    "links": {
        "next": "https://api.sandbox.junction.dev/places/types?page%5Bcursor%5D=ABC%3D%3D&page%5Blimit%5D=20"
    }
}
```

**Hooray!**

*If you want to skip to a guide on creating a booking order then follow this [**link here**](/docs/resellers/guides/create-an-order)*

---

### Didn't quite work?

Please refer back to the previous steps to make sure you set up everything correctly or please contact us.

#### Debugging

<ol>
    <li>
    <details>
        <summary>Is your command correct?</summary>
        1. Did you remember to replace `<YOUR_ACCESS_TOKEN>` in the curl command with your generated access token?
        2. Is the host correct? `https://api.sandbox.junction.dev`
    </details>
    </li>
    <li>
    <details>
        <summary>Do you have internet connection?</summary>
            1. Confirm you are connected by pinging a URL
            ```
            ping -c 4 www.google.com
            ```
    </details>
    </li>
    <li>
    <details>
        <summary>Is there a proper oAuth response?</summary>
            1. If you receive this response, it means your token is invalid:
            ```json
            {
                "errors": [
                    {
                        "status": "401",
                        "title": "Unauthorized",
                        "detail": "No permission -- see authorization schemes"
                    }
                ]
            }
            ```
    </details>
    </li>

</ol>
