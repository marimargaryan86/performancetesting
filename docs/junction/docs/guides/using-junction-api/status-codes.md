---
sidebar_position: 3
---

# Handling Errors

Snowfall uses standard [**HTTP response codes**](https://httpstatuses.com/) to indicate the success or failure of API requests.

## Status Codes

| Code | Reason                   | Description                                                                                               |
| ---- | ------------------------ | --------------------------------------------------------------------------------------------------------- |
| [200](https://httpstatuses.com/200) | OK                    | The request was successful                                                                               |
| [201](https://httpstatuses.com/201) | Created               | The request was successful, and a new resource was created                                               |
| [202](https://httpstatuses.com/202) | Accepted              | The request was successful, but the processing hasn't been completed                                      |
| [204](https://httpstatuses.com/204) | No Content            | The request was successful, but there is no response to send back                                          |
| [400](https://httpstatuses.com/400) | Bad Request           | The request was invalid, for example due to missing headers                                               |
| [401](https://httpstatuses.com/401) | Unauthorized          | An access token wasn't provided, or the provided token was invalid                                         |
| [403](https://httpstatuses.com/403) | Forbidden             | A valid access token was provided, but it didn't have sufficient permissions                               |
| [404](https://httpstatuses.com/404) | Not Found             | The requested resource doesn't exist                                                                      |
| [406](https://httpstatuses.com/406) | Not Acceptable        | The response type you requested with your `Accept` header isn't supported                                  |
| [422](https://httpstatuses.com/422) | Unprocessable Entity  | A validation error occurred                                                                              |
| [429](https://httpstatuses.com/429) | Too Many Requests     | You made too many requests to the API in a short period of time                                            |
| [500](https://httpstatuses.com/500) | Internal Server Error | Something went wrong. Please contact our support team and attach the `request_id` to your message. You should not retry this request. |
| [502](https://httpstatuses.com/502) | Bad Gateway           | Bad gateway error. Please contact our support team and attach the `request_id` to your message. You should not retry this request. |
| [503](https://httpstatuses.com/503) | Service Unavailable   | There is a temporary issue with the server. If the error persists, please contact our support team and attach the `request_id` to your message. Please retry later. |
| [504](https://httpstatuses.com/504) | Gateway Timeout       | Gateway timeout error. If the error persists, please contact our support team and attach the `request_id` to your message. Please retry later. |


## Examples

### 200 Success

##### Singular Object Response Body Example:

```json
{
    "data": {
        "id": "00011aab-2b3c-4567-c789-ddde1e0ee123d",
    }
}
```

##### List Response Body Example:

```json
{
    "data": [
        {
            "id": "00011aab-2b3c-4567-c789-ddde1e0ee123d",
        }
    ],
    "links": {
        "next": ""
    }
}
```

### 400 Bad Request

##### Response Body Example:

```json
{
    "errors": [
        {
            "status": "400",
            "title": "Bad Request",
            "detail": "Bad request syntax or unsupported method"
        }
    ]
}
```

### 404 Not found

##### Response Body Example:

```json
{
    "errors": [
        {
            "status": "404",
            "title": "Not Found",
            "detail": "Nothing matches the given URI"
        }
    ]
}
```
