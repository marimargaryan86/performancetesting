import type { OrderModel, OrderPassengerModel, TravelerDocumentModel } from "models/booking/order";
import type { CreateOrderModel } from "../models";
import type {
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
import type { JourneyModel } from "models/order";
import type { CabinClassModel, LegTypeModel } from "models/booking/offer";
import type { BookingDetailsModel } from "models/booking";

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

export function parseOrderSchema(data: OrderSchema): OrderModel {
  return {
    id: data.id,
    passengers: data.attributes.passengers.map((item) => parseOrderPassengerSchema(item)),
    bookingIds: data.relationships.bookings.data.map((item) => item.id),
    journeyId: data.relationships.journey.data.id,
    paymentId: data.relationships.payment.data.id,
  };
}

export function parseCreateOrderResponseSchema(data: CreateOrderResponseSchema): OrderModel {
  return parseOrderSchema(data.data);
}

export function parseGetOrderResponseSchema(data: GetOrderResponseSchema): OrderModel {
  const journeys: JourneyModel[] = [];
  const cabinClasses: CabinClassModel[] = [];
  const legTypes: LegTypeModel[] = [];
  const bookingDetails: BookingDetailsModel[] = [];
  const bookings: unknown[] = [];

  data.included?.forEach((item) => {
    if (item.type === "journeys") {
      journeys.push(parseJourneySchema(item));
    } else if (item.type === "cabin-classes") {
      cabinClasses.push(parseCabinClassSchema(item));
    } else if (item.type === "leg-types") {
      legTypes.push(parseLegTypeSchema(item));
    } else if (item.type === "trip-booking-details") {
      bookingDetails.push(parseBookingDetailsSchema(item));
    } else if (item.type === "trip-bookings") {
      bookings.push(parseBookingSchema(item));
    }
  });

  return parseOrderSchema(data.data);
}
