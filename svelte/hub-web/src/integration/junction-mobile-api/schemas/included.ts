import {
  legTypeParser,
  type LegType,
  type LegTypeSchema,
} from "integration/common/schemas/leg-type";
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
import {
  cabinClassParser,
  type CabinClass,
  type CabinClassSchema,
} from "integration/common/schemas/cabin-class";
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

type IncludedBind = {
  offers: { schema: OfferSchema; model: Offer };
  groups: { schema: OfferGroupSchema; model: OfferGroup };
  offerOptions: { schema: OfferOptionSchema; model: OfferOption };
  tripOfferGroupDetails: { schema: TripOfferGroupDetailsSchema; model: TripOfferGroupDetails };
  legTypes: { schema: LegTypeSchema; model: LegType };
  tripOfferOptionDetails: { schema: TripOfferOptionDetailsSchema; model: TripOfferOptionDetails };
  cabinClasses: { schema: CabinClassSchema; model: CabinClass };
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
  legTypes: { type: "leg-types", parser: legTypeParser },
  tripOfferOptionDetails: {
    type: "trip-offer-option-details",
    parser: tripOfferOptionDetailsParser,
  },
  cabinClasses: { type: "cabin-classes", parser: cabinClassParser },
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
    const key = Object.entries(parserMapping).find(([, { type }]) => type === item.type)?.[0] as
      | keyof IncludedBind
      | undefined;

    if (!key) {
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    schemaMapping[key].push(item as any);
    modelMapping[key].push({ id: item.id });
  });

  (Object.entries(modelMapping) as unknown as [keyof IncludedMapping, { id: string }[]][]).forEach(
    ([key, val]) => {
      val.forEach((item) => {
        const schema = (schemaMapping[key] as { id: string }[]).find(
          (inner) => inner.id === item.id,
        );

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        Object.assign(item, parserMapping[key].parser.toModel(schema as any, modelMapping as any));
      });
    },
  );

  return modelMapping as unknown as IncludedMapping;
}
