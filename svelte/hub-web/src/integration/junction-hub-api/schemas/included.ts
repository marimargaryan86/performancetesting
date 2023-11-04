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
import { cabinClassParser, type CabinClass, type CabinClassSchema } from "./cabin-class";
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
import { legTypeParser, type LegType, type LegTypeSchema } from "./leg-type";
import { orderParser, type Order, type OrderSchema } from "./order";
import { transactionParser, type Transaction, type TransactionSchema } from "./transaction";

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
  cabinClasses: { schema: CabinClassSchema; model: CabinClass };
  legTypes: { schema: LegTypeSchema; model: LegType };
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
  cabinClasses: { type: "cabin-classes", parser: cabinClassParser },
  legTypes: { type: "leg-types", parser: legTypeParser },
};

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
