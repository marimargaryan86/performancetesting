const placesRoot = "/places";
const curatedPlaces = `${placesRoot}/curated`;
const ordersRoot = "/orders";
const order = (orderId: string) => `${ordersRoot}/${orderId}`;
const orderItem = (orderId: string, orderItemId: string) => `${order(orderId)}/${orderItemId}`;
const orderTrip = (orderId: string, orderItemId: string, tripId: string) =>
  `${order(orderId)}/${orderItemId}/${tripId}`;
const resellersRoot = "/resellers";
const reseller = (resellerId: string) => `${resellersRoot}/${resellerId}`;
const providersRoot = "/providers";
const provider = (providerId: string) => `${providersRoot}/${providerId}`;

export default {
  places: {
    root: placesRoot,
    curatedPlaces,
  },
  orders: {
    root: ordersRoot,
    order,
    item: orderItem,
    trip: orderTrip,
  },
  resellers: {
    root: resellersRoot,
    reseller,
  },
  providers: {
    root: providersRoot,
    provider,
  },
};
