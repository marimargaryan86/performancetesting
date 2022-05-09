const placesRoot = "/places";
const curatedPlaces = `${placesRoot}/curated`;
const ordersRoot = "/orders";
const order = (orderId: string) => `${ordersRoot}/${orderId}`;
const orderItem = (orderId: string, orderItemId: string) => `${order(orderId)}/${orderItemId}`;
const orderTrip = (orderId: string, orderItemId: string, tripId: string) =>
  `${order(orderId)}/${orderItemId}/${tripId}`;

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
};
