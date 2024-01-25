# OpenAPI

Our APIs follow the [JSON:API](https://jsonapi.org) specification.

## String Formats

We support the following `format` values for `"type": "string"` properties:

| Format      | Specification                                                         | Example                                |
|-------------|-----------------------------------------------------------------------|----------------------------------------|
| `country`   | [ISO 3166-1 alpha-2](https://www.iso.org/iso-3166-country-codes.html) | `NL`                                   |
| `currency`  | [ISO 4127](https://www.iso.org/iso-4217-currency-codes.html)          | `SEK`                                  |
| `date-time` | [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339)             | `2022-05-12T10:17:28.343Z`             |
| `email`     | [RFC 6531](https://datatracker.ietf.org/doc/html/rfc6531)             | `foobar@example.com`                   |
| `phone`     | [E.164 (international) format](https://www.itu.int/rec/T-REC-E.164)   | `+442085664503`                        |
| `uuid`      | [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122)             | `72e908f4-63c4-41b4-9f7e-977187799016` |


## Sorting

Sorting can be added to a resource by defining a query parameter:

```json
{
  "components": {
    "parameters": {
      "exampleSort": {
        "name": "sort",
        "in": "query",
        "required": false,
        "schema": {
          "type": "string",
          "enum": [
            "id",
            "-id",
            "title",
            "-title"
          ],
          "default": "id",
          "example": "id"
        },
        "description": "Customize which field to sort examples by.",
        "style": "form",
        "explode": false
      }
    }
  }
}
```

Then add it to endpoint's `parameters`.

```json
{
  "paths": {
    "/examples": {
      "parameters": [
        {
          "$ref": "#/components/parameters/exampleSort"
        }
      ]
    }
  }
}
```

Every value that can be sorted on should be an attribute of the resource.

Also see the related [example implementation](../../standard-library/python/sorting.md)

## Filtering

The simplest filter to use is the exact filter, using the `eq` operator:
`?filter[field][eq]=value`

A list of allowed operators are:

* `eq` - Equal to
* `ne` - Not equal to
* `gt` - Greater than
* `lt` - Lesser than
* `ge` - Greater than or equal
* `le` - Lesser than or equal
* `like` - Partial match. Should match using `/value/i` to get
  case-insensitive partial matching.

If a user applies multiple filters, all must validate for the resource to
be returned, meaning they _must_ be implemented as `AND`, _never_ as `OR`.

:::tip

Because of the restriction that all filters must be used as `AND` multiple
`like` filters on the same endpoint makes little sense, consider
solving searching for resources with a dedicated search endpoint.

:::

:::caution

Think twice before deciding to add filters. Some of them can be quite
taxing on MongoDB. It's important to analyze how the filter is being used in
conjunction with sort parameters to figure out the most efficient
compound indexes to create for the collection.

:::

:::danger

Be vary when adding filters for an attribute of a relationship, because that
data might reside in a different service than the resource being filtered,
meaning it's virtually impossible to have proper filtering that also supports
sorting and pagination.

:::

### Operator examples

#### Match field again array

Filter on `field` being either `foo` or `bar`:

```?filter[field][eq]=foo,bar```

#### Datetime range

Filter on `created_at` being between two datetimes:

```
?filter[created_at][ge]=2010-10-10T10:10:10Z&filter[created_at][le]=2011-11-11T11:11:11Z
```

#### Date range

Filter on `birthDate` being between two dates:

```
?filter[birthDate][ge]=2010-10-10&filter[birthDate][le]=2011-11-11
```

#### Partial match

Filter on `name` containing the string `foo`:

```
?filter[name][like]=foo
```

### Filter parameter definition example

#### eq

```json
{
  "components": {
    "parameters": {
      "filterExampleFieldEq": {
        "name": "filter[field][eq]",
        "in": "query",
        "required": false,
        "schema": {
          "type": "array",
          "items": {
            "type": "string",
            "example": "foo"
          },
          "example": [
            "foo"
          ]
        },
        "description": "Filters examples based on the value of field",
        "style": "form",
        "explode": false
      }
    }
  }
}
```

#### le

```json
{
  "components": {
    "parameters": {
      "filterCreateAtEq": {
        "name": "filter[createdAt][le]",
        "in": "query",
        "required": false,
        "schema": {
          "type": "string",
          "format": "date-time",
          "example": "2019-08-24T14:15:22Z"
        },
        "description": "Filters resources where created at is less than or equal to value"
      }
    }
  }
}
```

#### like

```json
{
  "components": {
    "parameters": {
      "filterCreateAtEq": {
        "name": "filter[field][like]",
        "in": "query",
        "required": false,
        "schema": {
          "type": "string",
          "minLength": 3,
          "example": "foo"
        },
        "description": "Filters resources where created at is less than or equal to value"
      }
    }
  }
}
```
