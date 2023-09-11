import type {
  BookingDetailsModel,
  BookingDetailsSchema,
  BookingModel,
  BookingSchema,
} from "../schemas/booking";
import type { JourneyModel, JourneySchema } from "../schemas/journey";
import {
  legTypeModel,
  type OfferIncludes,
  type TripOfferPriceQuoteIncludes,
  cabinClassModel,
  type LegTypeModel,
  type LegTypeSchema,
  type CabinClassModel,
  type CabinClassSchema,
  type TripOfferGroupDetailsModel,
  type TripOfferGroupDetailsSchema,
  type TripOfferOptionDetailsModel,
  type TripOfferOptionDetailsSchema,
  type OfferOptionModel,
  type OfferOptionSchema,
  type OfferGroupModel,
  type OfferGroupSchema,
  type OfferModel,
  type OfferSchema,
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
  data?: (OrderIncludes | TripOfferPriceQuoteIncludes | OfferIncludes)[],
): {
  legTypes: LegTypeModel[];
  offerGroupDetails: TripOfferGroupDetailsModel[];
  cabinClasses: CabinClassModel[];
  offerOptionDetails: TripOfferOptionDetailsModel[];
  offerOptions: OfferOptionModel[];
  offerGroups: OfferGroupModel[];
  offers: OfferModel[];
  journeys: JourneyModel[];
  bookingDetails: BookingDetailsModel[];
  bookings: BookingModel[];
} {
  const legTypes_: LegTypeSchema[] = [];
  const offerGroupDetails_: TripOfferGroupDetailsSchema[] = [];
  const cabinClasses_: CabinClassSchema[] = [];
  const offerOptionDetails_: TripOfferOptionDetailsSchema[] = [];
  const offerOptions_: OfferOptionSchema[] = [];
  const offerGroups_: OfferGroupSchema[] = [];
  const offers_: OfferSchema[] = [];
  const journeys_: JourneySchema[] = [];
  const bookingDetails_: BookingDetailsSchema[] = [];
  const bookings_: BookingSchema[] = [];

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
