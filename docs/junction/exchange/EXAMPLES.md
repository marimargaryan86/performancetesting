# Examples

## Booking Flow

Before starting it's recommended to retrieve all places from the [List Places](../../openapi/client_api/openapi.json/paths/~1places/get) endpoint and keep them in a local cache for better performance of your application.

1. Create a new Trip Search using the [New Trip Search](../../openapi/client_api/openapi.json/paths/~1trips~1searches/post) endpoint, providing an origin, a destination and a departure time. This request will initiate an asynchronous search in the system and the response will thus only contain metadata about the trip search itself - it won't contain any actual trips.
2. Using the ID of the Trip Search from the previous step, we can call [List Trips by Trip Search](../../openapi/client_api/openapi.json/paths/~1trips~1searches~1{tripSearchId}~1trips/get) to retrieve all trips found by our search so far. Remember, since the search process is asynchronous, it could take several seconds before all trip results are available (if any are found at all).
3. Once we've found a trip we want to book, we need to search for offers for it. This is done through the [New Offer Search](../../openapi/client_api/openapi.json/paths/~1offers~1searches/post) endpoint. Just like the trip search, this request will initiate an asynchronous search in the system and the response will thus only contain metadata about the offer search itself.
4. Using the ID of the Offer Search from the previous step, we can call  [List Offers by Offer Search](../../openapi/client_api/openapi.json/paths/~1offers~1searches~1{offerSearchId}~1offers/get) to retrieve all offers found by our search so far. Remember, since the search process is asynchronous, it could take several seconds before all offer results are available (if any are found at all).
5. Once we've picked an offer for our trip, we can book it using the [New Order](../../openapi/client_api/openapi.json/paths/~1orders/post) endpoint. This endpoint requires the ID of offer aggregate we picked, the ID of exactly one offer from each offer group within the aggregate, as well as details about the passengers travelling.
6. Calling [View Order](../../openapi/client_api/openapi.json/paths/~1orders~1{orderId}/get) will let us check the status of our order and, once it's completed, view addtional details about it.
