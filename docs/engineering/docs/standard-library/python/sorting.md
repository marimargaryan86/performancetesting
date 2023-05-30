# Sorting

It's relatively simple to incorporate sorting for specific fields to our API.
This document will illustrate that with a list of changes that can be applied.

## Necessary changes

All that is required is a parameter in our OpenAPI specification, a small
change to the related Protocol Buffer request message specification, some
mapping and the use of some helpers.

### OpenAPI

We might have the endpoint `/examples` that return an `Example` resource
that has an `id` and a `title` field. We will want to create a sort
parameter (unless there already is one):

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

If there already is a sort parameter, and we just want to extend the
sorting capabilities of an endpoint, just add our new fields to the
enumeration array.

:::info

Notice that we currently only support sorting on one field at a time.

:::

### Protocol Buffers

In the file defining the gRPC service(s) of the service we want to change,
find the corresponding endpoint that our API service is calling.

Unless already there, add a line to import `snowfall/stdlib/v1/sort.proto`:

```protobuf
import "snowfall/stdlib/v1/sort.proto";
```

Then in the request message add `snowfall.stdlib.v1.Sort sort_by = ?;` with
the appropriate index, unless already present, like so:

```protobuf
message ListExamplesRequest {
  int32 page_size = 1;
  string page_token = 2;
  // highlight-next-line
  snowfall.stdlib.v1.Sort sort_by = 3;
}
```

### API service

In our API service, we will need to construct a
`snowfall.stdlib.v1.sort_pb2.Sort` object to pass to the gRPC request.

There is a helper function in our standard library for this,
`snowfall.stdlib.integration.starlette.sorting.get_sort()`. All we need to
provide is a mapping between what the field in the OpenAPI specification and
the field in the protocol buffer message is.

In this case, the protocol buffer message for `Example` does use the same
wording as the OpenAPI specification, the OpenAPI field `title` is mapped to
the protocol buffer message field `name` of the `Example` message.

On the endpoint class, we add this mapping:

```python
class Examples(object):
    # highlight-start
    _sort = {
        "id": "id",
        "title": "name",
    }
    # highlight-end
```

We can then use it with the helper method to create the `sort_pb2.Sort` object,
along with a `starlette.requests.Request` object, like so:

```python
sorting.get_sort(request, self._sort)
```

If we are using an adapter class to wrap the gRPC client, make sure to
update that to accept the `sort_pb2.Sort` object.

### gRPC service

What we need to do in the gRPC server is very similar to what we did in the
API service.

To further de-couple our data models, we are in this example not using the same
protocol buffer message for storage as we are for gRPC communication,
resulting in the `name` field of the gRPC model to have to be mapped to the
`label` field in our storage model.

#### Repository

In the repository, we will need to make sure that the field we want to sort
on is indexed, making sure that there is an index in `_indexes` looking like
`pymongo.IndexModel("label", background=True)`.

How the sort argument is passed depends on exactly how the resources are
fetched.

If it's by using the `all_()` method from `AllMixin`, then we just
have to pass it the sort argument.

If instead it's implemented with a custom method, we will have to
add the `sort` argument and pass it along to `_find_with_cursor()`, like so:

```python
    async def find(
        self,
        cursor: str,
        # highlight-next-line
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[Example]:
        return await self._find_with_cursor(
            cur=cursor,
            # highlight-next-line
            sort=sort,
        )
```

#### gRPC service

In the gRPC service class we want to add a mapping and use it to process the
`sort_pb2.Sort` message in the request using the
`snowfall.stdlib.transport.grpc.sorting.get_sort()` helper function in
standard library.

```python
class ExampleService(
    service.Service,
    examples_pb2_grpc.ExampleServiceServicer,
):
    # highlight-start
    _sort = {
        "id": "_id",
        "name": "label",
    }
    # highlight-end
```

After that we can use it in our endpoint method before passing the sort
tuple to our repository method like so:

```python
sorting.get_sort(request.sort_by, self._sort)
```

## Merge request example

There is a [merge request](https://git.snowfall.se/junction/junction/-/merge_requests/2246/diffs)
with an example of adding sorting for the `id` and `reference` fields of the
`Journey` resources.
