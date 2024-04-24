import {
  offerParser,
  type Offer,
  type OfferSchema,
  type OfferGroupSchema,
  type OfferGroup,
  offerGroupParser,
  type OfferOptionSchema,
  type OfferOption,
  offerOptionParser,
  type TripOfferGroupDetailsSchema,
  type TripOfferGroupDetails,
  tripOfferGroupDetailsParser,
  type TripOfferOptionDetailsSchema,
  type TripOfferOptionDetails,
  tripOfferOptionDetailsParser,
} from "./offer";
import * as CommonSchemas from "~/integration/common/schemas";
import {
  paymentParser,
  type Payment,
  type PaymentSchema,
  type VoucherSchema,
  type Voucher,
  voucherParser,
} from "./payment";
import { orderParser, type Order, type OrderSchema } from "./order";
import { journeyParser, type Journey, type JourneySchema } from "./journey";
import {
  tripBookingParser,
  type TripBooking,
  type TripBookingSchema,
  type TripBookingDetailsSchema,
  type TripBookingDetails,
  tripBookingDetailsParser,
} from "./booking";
import {
  cancellationRequestParsers,
  type CancellationRequest,
  type CancellationRequestSchema,
  type BookingCancellation,
  type BookingCancellationSchema,
  bookingCancellationParser,
} from "./cancellation";
import {
  tripOfferPriceQuoteParser,
  type TripOfferPriceQuote,
  type TripOfferPriceQuoteSchema,
} from "./trip-offer-price-quote";
import objectExt from "$lib/object-ext";

type IncludedBind = {
  offers: { schema: OfferSchema; model: Offer };
  groups: { schema: OfferGroupSchema; model: OfferGroup };
  offerOptions: { schema: OfferOptionSchema; model: OfferOption };
  tripOfferGroupDetails: { schema: TripOfferGroupDetailsSchema; model: TripOfferGroupDetails };
  legTypes: { schema: CommonSchemas.LegTypeSchema; model: CommonSchemas.LegType };
  tripOfferOptionDetails: { schema: TripOfferOptionDetailsSchema; model: TripOfferOptionDetails };
  cabinClasses: { schema: CommonSchemas.CabinClassSchema; model: CommonSchemas.CabinClass };
  payments: { schema: PaymentSchema; model: Payment };
  vouchers: { schema: VoucherSchema; model: Voucher };
  orders: { schema: OrderSchema; model: Order };
  journeys: { schema: JourneySchema; model: Journey };
  tripBookings: { schema: TripBookingSchema; model: TripBooking };
  tripBookingDetails: { schema: TripBookingDetailsSchema; model: TripBookingDetails };
  cancellationRequests: { schema: CancellationRequestSchema; model: CancellationRequest };
  tripOfferPriceQuotes: { schema: TripOfferPriceQuoteSchema; model: TripOfferPriceQuote };
  bookingCancellations: { schema: BookingCancellationSchema; model: BookingCancellation };
};

type IncludedSchemaMapping = { [key in keyof IncludedBind]?: IncludedBind[key]["schema"][] };

export type IncludedMapping = { [key in keyof IncludedBind]?: IncludedBind[key]["model"][] };
export type IncludedSchemas = {
  [key in keyof IncludedBind]: IncludedBind[key]["schema"];
}[keyof IncludedBind][];

const parserMapping: {
  [key in keyof IncludedBind]: {
    type: IncludedBind[key]["schema"]["type"];
    parser: {
      toModel: (
        data: IncludedBind[key]["schema"],
        included?: IncludedMapping,
      ) => IncludedBind[key]["model"];
    };
  };
} = {
  offers: { type: "offers", parser: offerParser },
  groups: { type: "offer-groups", parser: offerGroupParser },
  offerOptions: { type: "offer-options", parser: offerOptionParser },
  tripOfferGroupDetails: { type: "trip-offer-group-details", parser: tripOfferGroupDetailsParser },
  legTypes: { type: "leg-types", parser: CommonSchemas.legTypeParser },
  tripOfferOptionDetails: {
    type: "trip-offer-option-details",
    parser: tripOfferOptionDetailsParser,
  },
  cabinClasses: { type: "cabin-classes", parser: CommonSchemas.cabinClassParser },
  payments: { type: "payments", parser: paymentParser },
  vouchers: { type: "vouchers", parser: voucherParser },
  orders: { type: "orders", parser: orderParser },
  journeys: { type: "journeys", parser: journeyParser },
  tripBookings: { type: "trip-bookings", parser: tripBookingParser },
  tripBookingDetails: { type: "trip-booking-details", parser: tripBookingDetailsParser },
  cancellationRequests: { type: "cancellation-request", parser: cancellationRequestParsers },
  tripOfferPriceQuotes: { type: "trip-offer-price-quotes", parser: tripOfferPriceQuoteParser },
  bookingCancellations: { type: "booking-cancellation", parser: bookingCancellationParser },
};

function sortLegs(a: CommonSchemas.OfferSegmentLeg, b: CommonSchemas.OfferSegmentLeg): number {
  return a.departureAt.getTime() - b.departureAt.getTime();
}

function sortBookingDetails(a: TripBookingDetails, b: TripBookingDetails): number {
  return (a.legs[0]?.departureAt.getTime() ?? 0) - (b.legs.at(-1)?.departureAt.getTime() ?? 0);
}

function sortOfferGroupDetails(a: TripOfferGroupDetails, b: TripOfferGroupDetails): number {
  return (
    a.sequences.trip * 1000 + a.sequences.segment - (b.sequences.trip * 1000 + b.sequences.segment)
  );
}

function sortOfferOptionDetails(a: TripOfferOptionDetails, b: TripOfferOptionDetails): number {
  if (!(a.details && b.details)) {
    return 0;
  }

  return (
    a.details.sequences.trip * 1000 +
    a.details.sequences.segment -
    (b.details.sequences.trip * 1000 + b.details.sequences.segment)
  );
}

function sortOfferOptions(a: OfferOption, b: OfferOption): number {
  return a.price.total.amount - b.price.total.amount;
}

function sortOfferGroups(a: OfferGroup, b: OfferGroup): number {
  return (
    (a.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
    (b.detailsList.at(-1)?.legs.at(-1)?.departureAt.getTime() ?? 0)
  );
}

function sortBookings(a: TripBooking, b: TripBooking): number {
  return (
    (a.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
    (b.detailsList.at(-1)?.legs.at(-1)?.departureAt.getTime() ?? 0)
  );
}

function sortOrders(a: Order, b: Order): number {
  return (
    (a.bookings[0]?.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
    (b.bookings.at(-1)?.detailsList.at(-1)?.legs.at(-1)?.departureAt.getTime() ?? 0)
  );
}

function orderIncluded(included: IncludedMapping): IncludedMapping {
  // Sort legs
  included.tripOfferGroupDetails?.forEach((item) => item.legs.sort(sortLegs));
  included.tripBookingDetails?.forEach((item) => item.legs.sort(sortLegs));
  // Sort details lists
  included.tripBookings?.forEach((item) => item.detailsList.sort(sortBookingDetails));
  included.offerOptions?.forEach((item) => item.detailsList.sort(sortOfferOptionDetails));
  // Sort options
  included.groups?.forEach((item) => {
    item.detailsList.sort(sortOfferGroupDetails);
    item.options.sort(sortOfferOptions);
  });
  included.tripOfferPriceQuotes?.forEach((item) => item.options.sort(sortOfferOptions));
  included.offers?.forEach((item) => item.groups.sort(sortOfferGroups));
  included.cancellationRequests?.forEach((item) => item.bookings.sort(sortBookings));
  included.orders?.forEach((item) => item.bookings.sort(sortBookings));
  included.journeys?.forEach((item) => item.orders.sort(sortOrders));
  // Offers
  included.offers?.sort(
    (a, b) =>
      (a.groups[0]?.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
      (b.groups[0]?.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0),
  );

  return included;
}

// eslint-disable-next-line max-lines-per-function
export function parseIncluded(included?: IncludedSchemas): IncludedMapping {
  const schemaMapping: Required<IncludedSchemaMapping> = {
    offers: [],
    groups: [],
    offerOptions: [],
    tripOfferGroupDetails: [],
    legTypes: [],
    tripOfferOptionDetails: [],
    cabinClasses: [],
    payments: [],
    vouchers: [],
    orders: [],
    journeys: [],
    tripBookings: [],
    tripBookingDetails: [],
    cancellationRequests: [],
    tripOfferPriceQuotes: [],
    bookingCancellations: [],
  };

  const modelMapping: { [key in keyof IncludedMapping]-?: { id: string }[] } = {
    offers: [],
    groups: [],
    offerOptions: [],
    tripOfferGroupDetails: [],
    legTypes: [],
    tripOfferOptionDetails: [],
    cabinClasses: [],
    payments: [],
    vouchers: [],
    orders: [],
    journeys: [],
    tripBookings: [],
    tripBookingDetails: [],
    cancellationRequests: [],
    tripOfferPriceQuotes: [],
    bookingCancellations: [],
  };

  included?.forEach((item) => {
    const key = objectExt.entries(parserMapping).find(([, { type }]) => type === item.type)?.[0];

    if (!key) {
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    schemaMapping[key].push(item as any);
    modelMapping[key].push({ id: item.id });
  });

  objectExt.entries(modelMapping).forEach(([key, val]) => {
    val.forEach((item) => {
      const schema = (schemaMapping[key] as { id: string }[]).find((inner) => inner.id === item.id);

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      Object.assign(item, parserMapping[key].parser.toModel(schema as any, modelMapping as any));
    });
  });

  return orderIncluded(modelMapping as unknown as IncludedMapping);
}
