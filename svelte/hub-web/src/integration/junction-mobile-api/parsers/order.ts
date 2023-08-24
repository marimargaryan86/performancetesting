import type {
  BookingModel,
  JourneyModel,
  OrderModel,
  OrderPassengerModel,
  TravelerDocumentModel,
} from "models/booking/order";
import type { CreateOrderModel } from "../models";
import type {
  BookingDetailsSchema,
  BookingSchema,
  CreateOrderRequestSchema,
  CreateOrderResponseSchema,
  GetOrderResponseSchema,
  OrderPassengerSchema,
  OrderSchema,
  TravelerDocumentSchema,
} from "../schemas/order";
import { parseJourneySchema } from "./journey";
import { parseCabinClassSchema, parseLegTypeSchema } from "./offer";
import { parseBookingDetailsSchema, parseBookingSchema } from "./booking";
import type { JourneySchema } from "../schemas/journey";
import type { CabinClassSchema, LegTypeSchema } from "../schemas/offer";

export function parseTravelerDocumentModel(
  data: NonNullable<CreateOrderModel["passengers"][number]["travelerDocument"]>,
): TravelerDocumentSchema {
  if (data.type === "passport") {
    return {
      documentType: "passport",
      documentNumber: data.number,
    };
  }

  throw new Error(`Unknown document type "${data.type}"`);
}

export function parseCreateOrderModel(data: CreateOrderModel): CreateOrderRequestSchema {
  return {
    data: {
      type: "orders",
      attributes: {
        passengers: data.passengers.map((item) => ({
          firstName: item.firstName,
          lastName: item.lastName,
          dateOfBirth: item.dateOfBirth.toLocaleDateString("sv-SE"),
          gender: item.gender,
          title: item.title,
          travelerDocument: item.travelerDocument
            ? parseTravelerDocumentModel(item.travelerDocument)
            : undefined,
        })),
        contactDetails: {
          address: {
            addressLines: data.contactDetails.address.addressLines,
            city: data.contactDetails.address.city,
            countryCode: data.contactDetails.address.countryCode,
            postalCode: data.contactDetails.address.postalCode,
          },
          email: data.contactDetails.email,
          phoneNumber: `${data.contactDetails.phone.countryCode}${data.contactDetails.phone.number}`,
        },
      },
      relationships: {
        quote: { data: { id: data.priceQuoteId, type: "trip-offer-price-quotes" } },
        payment: { data: { id: data.paymentId, type: "payments" } },
      },
    },
  };
}

export function parseTravelerDocumentSchema(data: TravelerDocumentSchema): TravelerDocumentModel {
  if (data.documentType === "passport") {
    return {
      type: "passport",
      number: data.documentNumber,
    };
  }

  throw new Error(`Unknown document type "${data.documentType}"`);
}

export function parseOrderPassengerSchema(data: OrderPassengerSchema): OrderPassengerModel {
  return {
    firstName: data.firstName,
    lastName: data.lastName,
    title: data.title,
    gender: data.gender,
    dateOfBirth: new Date(data.dateOfBirth),
    document: data.travelerDocument
      ? parseTravelerDocumentSchema(data.travelerDocument)
      : undefined,
  };
}

export function parseOrderSchema(
  data: OrderSchema,
  journeys: JourneyModel[],
  bookings: BookingModel[],
): OrderModel {
  const bookingIds = data.relationships.bookings.data.map((item) => item.id);

  return {
    id: data.id,
    passengers: data.attributes.passengers.map((item) => parseOrderPassengerSchema(item)),
    bookingIds,
    bookings: bookings.filter((item) => bookingIds.includes(item.id)),
    journeyId: data.relationships.journey.data.id,
    journey: journeys.find((item) => item.id === data.relationships.journey.data.id),
    paymentId: data.relationships.payment.data.id,
  };
}

export function parseCreateOrderResponseSchema(data: CreateOrderResponseSchema): OrderModel {
  return parseOrderSchema(data.data, [], []);
}

export function parseGetOrderResponseSchema(data: GetOrderResponseSchema): OrderModel {
  const journeys: JourneySchema[] = [];
  const cabinClasses: CabinClassSchema[] = [];
  const legTypes: LegTypeSchema[] = [];
  const bookingDetails: BookingDetailsSchema[] = [];
  const bookings: BookingSchema[] = [];

  data.included?.forEach((item) => {
    if (item.type === "journeys") {
      journeys.push(item);
    } else if (item.type === "cabin-classes") {
      cabinClasses.push(item);
    } else if (item.type === "leg-types") {
      legTypes.push(item);
    } else if (item.type === "trip-booking-details") {
      bookingDetails.push(item);
    } else if (item.type === "trip-bookings") {
      bookings.push(item);
    }
  });

  const journeys_ = journeys.map((item) => parseJourneySchema(item, []));
  const cabinClasses_ = cabinClasses.map(parseCabinClassSchema);
  const legTypes_ = legTypes.map(parseLegTypeSchema);
  const bookingDetails_ = bookingDetails.map((item) =>
    parseBookingDetailsSchema(item, {
      bookings: [],
      cabinClasses: cabinClasses_,
      legTypes: legTypes_,
    }),
  );
  const bookings_ = bookings.map((item) => parseBookingSchema(item, bookingDetails_, []));

  return parseOrderSchema(data.data, journeys_, bookings_);
}
