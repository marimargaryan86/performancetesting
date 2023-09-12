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

type IncludeSchemas = {
  legTypes: LegTypeSchema[];
  offerGroupDetails: TripOfferGroupDetailsSchema[];
  cabinClasses: CabinClassSchema[];
  offerOptionDetails: TripOfferOptionDetailsSchema[];
  offerOptions: OfferOptionSchema[];
  offerGroups: OfferGroupSchema[];
  offers: OfferSchema[];
  journeys: JourneySchema[];
  bookingDetails: BookingDetailsSchema[];
  bookings: BookingSchema[];
};

type IncludeModels = {
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
};

function separateIncluded(
  data?: (OrderIncludes | TripOfferPriceQuoteIncludes | OfferIncludes)[],
): IncludeSchemas {
  const result: IncludeSchemas = {
    legTypes: [],
    offerGroupDetails: [],
    cabinClasses: [],
    offerOptionDetails: [],
    offerOptions: [],
    offerGroups: [],
    offers: [],
    journeys: [],
    bookingDetails: [],
    bookings: [],
  };

  // eslint-disable-next-line complexity
  data?.forEach((item) => {
    if (item.type === "leg-types") {
      result.legTypes.push(item);
    } else if (item.type === "trip-offer-group-details") {
      result.offerGroupDetails.push(item);
    } else if (item.type === "cabin-classes") {
      result.cabinClasses.push(item);
    } else if (item.type === "trip-offer-option-details") {
      result.offerOptionDetails.push(item);
    } else if (item.type === "offer-options") {
      result.offerOptions.push(item);
    } else if (item.type === "offer-groups") {
      result.offerGroups.push(item);
    } else if (item.type === "offers") {
      result.offers.push(item);
    } else if (item.type === "journeys") {
      result.journeys.push(item);
    } else if (item.type === "trip-booking-details") {
      result.bookingDetails.push(item);
    } else {
      result.bookings.push(item);
    }
  });

  return result;
}

export function parseIncluded(
  data?: (OrderIncludes | TripOfferPriceQuoteIncludes | OfferIncludes)[],
): IncludeModels {
  const mapping = separateIncluded(data);

  const legTypes = mapping.legTypes.map(legTypeModel.toModel);
  const offerGroupDetails = mapping.offerGroupDetails.map((item) =>
    parseOfferGroupDetailsSchema(item, { legTypes }),
  );
  const cabinClasses = mapping.cabinClasses.map(cabinClassModel.toModel);
  const offerOptionDetails = mapping.offerOptionDetails.map((item) =>
    parseOfferOptionDetailsSchema(item, { cabinClasses }),
  );
  const offerOptions = mapping.offerOptions.map((item) =>
    parseOfferOptionSchema(item, { offerOptionDetails }),
  );
  const offerGroups = mapping.offerGroups.map((item) =>
    parseOfferGroupSchema(item, { offerOptions, offerGroupDetails }),
  );
  const offers = mapping.offers.map((item) => parseOfferSchema(item, { offerGroups }));
  const journeys = mapping.journeys.map((item) => parseJourneySchema(item, { orders: [] }));
  const bookingDetails = mapping.bookingDetails.map((item) =>
    parseBookingDetailsSchema(item, {
      bookings: [],
      cabinClasses,
      legTypes,
    }),
  );
  const bookings = mapping.bookings.map((item) =>
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
