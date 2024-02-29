import { accountParser, type Account, type AccountSchema } from "./account";
import { billParser, type Bill, type BillSchema } from "./bill";
import {
  tripBookingDetailsParser,
  type TripBooking,
  type TripBookingDetails,
  type TripBookingDetailsSchema,
  type TripBookingSchema,
  tripBookingParser,
} from "./booking";
import {
  bookingCancellationParser,
  type BookingCancellation,
  type BookingCancellationSchema,
} from "./cancellation";
import { companyParser, type Company, type CompanySchema } from "./company";
import { contactParser, type Contact, type ContactSchema } from "./contact";
import { conversionParser, type Conversion, type ConversionSchema } from "./conversion";
import { currencyParser, type Currency, type CurrencySchema } from "./currency";
import { journeyParser, type Journey, type JourneySchema } from "./journey";
import * as CommonSchemas from "~/integration/common/schemas";
import { orderParser, type Order, type OrderSchema } from "./order";
import { transactionParser, type Transaction, type TransactionSchema } from "./transaction";
import { refundParser, type Refund, type RefundSchema } from "./refund";

type IncludedBind = {
  companies: { schema: CompanySchema; model: Company };
  contacts: { schema: ContactSchema; model: Contact };
  accounts: { schema: AccountSchema; model: Account };
  currencies: { schema: CurrencySchema; model: Currency };
  orders: { schema: OrderSchema; model: Order };
  transactions: { schema: TransactionSchema; model: Transaction };
  conversions: { schema: ConversionSchema; model: Conversion };
  bills: { schema: BillSchema; model: Bill };
  bookingCancellations: { schema: BookingCancellationSchema; model: BookingCancellation };
  tripBookingDetails: { schema: TripBookingDetailsSchema; model: TripBookingDetails };
  tripBookings: { schema: TripBookingSchema; model: TripBooking };
  journeys: { schema: JourneySchema; model: Journey };
  cabinClasses: { schema: CommonSchemas.CabinClassSchema; model: CommonSchemas.CabinClass };
  legTypes: { schema: CommonSchemas.LegTypeSchema; model: CommonSchemas.LegType };
  refunds: { schema: RefundSchema; model: Refund };
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
  companies: { type: "companies", parser: companyParser },
  contacts: { type: "contacts", parser: contactParser },
  accounts: { type: "accounts", parser: accountParser },
  currencies: { type: "currencies", parser: currencyParser },
  orders: { type: "orders", parser: orderParser },
  transactions: { type: "transactions", parser: transactionParser },
  conversions: { type: "conversions", parser: conversionParser },
  bills: { type: "bills", parser: billParser },
  bookingCancellations: { type: "booking-cancellation", parser: bookingCancellationParser },
  tripBookingDetails: { type: "trip-booking-details", parser: tripBookingDetailsParser },
  tripBookings: { type: "trip-bookings", parser: tripBookingParser },
  journeys: { type: "journeys", parser: journeyParser },
  cabinClasses: { type: "cabin-classes", parser: CommonSchemas.cabinClassParser },
  legTypes: { type: "leg-types", parser: CommonSchemas.legTypeParser },
  refunds: { type: "refunds", parser: refundParser },
};

function orderIncluded(included: IncludedMapping): IncludedMapping {
  included.tripBookingDetails?.forEach((item) =>
    item.legs.sort((a, b) => a.departureAt.getTime() - b.departureAt.getTime()),
  );
  included.tripBookings?.forEach((item) =>
    item.detailsList.sort(
      (a, b) => (a.legs[0]?.departureAt.getTime() ?? 0) - (b.legs[0]?.departureAt.getTime() ?? 0),
    ),
  );
  included.orders?.forEach((item) =>
    item.bookings.sort(
      (a, b) =>
        (a.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
        (b.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0),
    ),
  );
  included.journeys?.forEach((item) =>
    item.orders.sort(
      (a, b) =>
        (a.bookings[0]?.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
        (b.bookings[0]?.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0),
    ),
  );
  included.journeys?.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  included.transactions?.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  included.orders?.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  included.conversions?.sort(
    (a, b) => (b.createdAt?.getTime() ?? 0) - (a.createdAt?.getTime() ?? 0),
  );
  included.bills?.sort((a, b) => (b.updatedAt?.getTime() ?? 0) - (a.updatedAt?.getTime() ?? 0));

  return included;
}

// eslint-disable-next-line max-lines-per-function
export function parseIncluded(included?: IncludedSchemas): IncludedMapping {
  const schemaMapping: Required<IncludedSchemaMapping> = {
    companies: [],
    contacts: [],
    accounts: [],
    currencies: [],
    orders: [],
    transactions: [],
    conversions: [],
    bills: [],
    bookingCancellations: [],
    tripBookingDetails: [],
    tripBookings: [],
    journeys: [],
    cabinClasses: [],
    legTypes: [],
    refunds: [],
  };

  const modelMapping: { [key in keyof IncludedMapping]-?: { id: string }[] } = {
    companies: [],
    contacts: [],
    accounts: [],
    currencies: [],
    orders: [],
    transactions: [],
    conversions: [],
    bills: [],
    bookingCancellations: [],
    tripBookingDetails: [],
    tripBookings: [],
    journeys: [],
    cabinClasses: [],
    legTypes: [],
    refunds: [],
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

  return orderIncluded(modelMapping as unknown as IncludedMapping);
}
