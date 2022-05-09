import OrderService from "./services/order-service";
import PlaceService from "./services/place-service";

const placeService = new PlaceService("");
const orderService = new OrderService("");

export default {
  placeService,
  orderService,
};
