import type { Infer } from "../schema-model.server";
import type { bookingDetailsModel, bookingModel } from "../schemas/booking";
import type { journeyModel } from "../schemas/journey";
import {
  legTypeModel,
  type OfferIncludes,
  type TripOfferPriceQuoteIncludes,
  cabinClassModel,
  type offerGroupModel,
  type offerOptionModel,
  type tripOfferGroupDetailsModel,
  type tripOfferOptionDetailsModel,
  offerModel,
} from "../schemas/offer";
import type { OrderIncludes } from "../schemas/order";
import { parseBookingDetailsSchema, parseBookingSchema } from "./booking";
import { parseJourneySchema } from "./journey";
import {
  parseOfferGroupDetailsSchema,
  parseOfferGroupSchema,
  parseOfferOptionDetailsSchema,
  parseOfferOptionSchema,
  parseOfferSchema,
} from "./offer";

// eslint-disable-next-line max-lines-per-function
export function parseIncluded(
  data?: (OrderIncludes[number] | TripOfferPriceQuoteIncludes[number] | OfferIncludes[number])[],
): {
  legTypes: Infer<typeof legTypeModel>[];
  offerGroupDetails: Infer<typeof tripOfferGroupDetailsModel>[];
  cabinClasses: Infer<typeof cabinClassModel>[];
  offerOptionDetails: Infer<typeof tripOfferOptionDetailsModel>[];
  offerOptions: Infer<typeof offerOptionModel>[];
  offerGroups: Infer<typeof offerGroupModel>[];
  offers: Infer<typeof offerModel>[];
  journeys: Infer<typeof journeyModel>[];
  bookingDetails: Infer<typeof bookingDetailsModel>[];
  bookings: Infer<typeof bookingModel>[];
} {
  const legTypes_: Infer<typeof legTypeModel, "schema">[] = [];
  const offerGroupDetails_: Infer<typeof tripOfferGroupDetailsModel, "schema">[] = [];
  const cabinClasses_: Infer<typeof cabinClassModel, "schema">[] = [];
  const offerOptionDetails_: Infer<typeof tripOfferOptionDetailsModel, "schema">[] = [];
  const offerOptions_: Infer<typeof offerOptionModel, "schema">[] = [];
  const offerGroups_: Infer<typeof offerGroupModel, "schema">[] = [];
  const offers_: Infer<typeof offerModel, "schema">[] = [];
  const journeys_: Infer<typeof journeyModel, "schema">[] = [];
  const bookingDetails_: Infer<typeof bookingDetailsModel, "schema">[] = [];
  const bookings_: Infer<typeof bookingModel, "schema">[] = [];

  // eslint-disable-next-line complexity
  data?.forEach((item) => {
    if (item.type === "leg-types") {
      legTypes_.push(item);
    } else if (item.type === "trip-offer-group-details") {
      offerGroupDetails_.push(item);
    } else if (item.type === "cabin-classes") {
      cabinClasses_.push(item);
    } else if (item.type === "trip-offer-option-details") {
      offerOptionDetails_.push(item);
    } else if (item.type === "offer-options") {
      offerOptions_.push(item);
    } else if (item.type === "offer-groups") {
      offerGroups_.push(item);
    } else if (item.type === "offers") {
      offers_.push(item);
    } else if (item.type === "journeys") {
      journeys_.push(item);
    } else if (item.type === "trip-booking-details") {
      bookingDetails_.push(item);
    } else {
      bookings_.push(item);
    }
  });

  const legTypes = legTypes_.map(legTypeModel.toModel);
  const offerGroupDetails = offerGroupDetails_.map((item) =>
    parseOfferGroupDetailsSchema(item, { legTypes }),
  );
  const cabinClasses = cabinClasses_.map(cabinClassModel.toModel);
  const offerOptionDetails = offerOptionDetails_.map((item) =>
    parseOfferOptionDetailsSchema(item, { cabinClasses }),
  );
  const offerOptions = offerOptions_.map((item) =>
    parseOfferOptionSchema(item, { offerOptionDetails }),
  );
  const offerGroups = offerGroups_.map((item) =>
    parseOfferGroupSchema(item, { offerOptions, offerGroupDetails }),
  );
  const offers = offers_.map((item) => parseOfferSchema(item, { offerGroups }));
  const journeys = journeys_.map((item) => parseJourneySchema(item, { orders: [] }));
  const bookingDetails = bookingDetails_.map((item) =>
    parseBookingDetailsSchema(item, {
      bookings: [],
      cabinClasses,
      legTypes,
    }),
  );
  const bookings = bookings_.map((item) =>
    parseBookingSchema(item, { bookingDetails, orders: [] }),
  );

  return {
    legTypes,
    offerGroupDetails,
    cabinClasses,
    offerOptionDetails,
    offerOptions,
    offerGroups,
    offers,
    journeys,
    bookingDetails,
    bookings,
  };
}
