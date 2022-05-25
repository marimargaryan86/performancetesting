import OrderService from "./services/order-service";
import PlaceService from "./services/place-service";
import ResellerService from "./services/reseller-service";
import ProviderService from "./services/provider-service";

const placeService = new PlaceService("");
const orderService = new OrderService("");
const resellerService = new ResellerService("");
const providerService = new ProviderService("");

export default {
  placeService,
  orderService,
  resellerService,
  providerService,
};
