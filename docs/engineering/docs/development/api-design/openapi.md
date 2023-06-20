# OpenAPI

Our APIs follow the [JSON:API](https://jsonapi.org) specification.

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

If a user applies multiple filters, all most validate for the resource to
be returned.

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

### Filter parameter definition example

Adding a simple `eq` filter for the `example` resource:

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
