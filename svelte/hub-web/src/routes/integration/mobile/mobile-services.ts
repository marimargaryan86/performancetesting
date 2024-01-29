import cancellationRequests from "./cancellation-requests/cancellation-request-service";
import offers from "./offers/offer-service";
import orders from "./orders/order-service";
import payments from "./payments/payment-service";
import places from "./places/place-service";
import trips from "./trips/trip-service";
import simpleOfferService from "./simple-offers/simple-offer-service";

export default {
  cancellationRequests,
  offers,
  orders,
  payments,
  places,
  trips,
  simpleOfferService,
};
