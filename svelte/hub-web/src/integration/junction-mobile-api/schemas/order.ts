import { tripOfferPriceQuoteModel, type LegTypeSchema, type CabinClassSchema } from "./offer";
import { z } from "zod";
import { paymentIntentModel } from "./payment";
import { journeyModel, type JourneySchema } from "./journey";
import { bookingModel, type BookingDetailsSchema, type BookingSchema } from "./booking";
import { priceModel } from "./price";
import schemaModel, { type Infer } from "utils/schema-model";

export const passengerTitle = z.enum(["unspecified", "mr", "mrs", "ms", "miss"]);
export const passengerGender = z.enum(["unspecified", "male", "female"]);

export const addressModel = z.object({
  addressLines: z.array(z.string()),
  countryCode: z.string(),
  postalCode: z.string(),
  city: z.string(),
});

export const contactDetailsModel = schemaModel.create({
  schema: z.object({
    email: z.string().email(),
    address: addressModel,
    phoneNumber: z.string(),
  }),
  model: z.object({
    address: addressModel,
    email: z.string().email(),
    phone: z.object({
      countryCode: z.string(),
      number: z.string(),
    }),
  }),
  toModel: (data) => ({ ...data, phone: { countryCode: "", number: data.phoneNumber } }),
  toSchema: (data) => ({ ...data, phoneNumber: `${data.phone.countryCode}${data.phone.number}` }),
});

export const passportDocumentModel = schemaModel.create({
  schema: z.object({
    documentType: z.enum(["passport"]),
    documentNumber: z.string().optional(),
    documentIssueCountry: z.string().optional(),
    documentExpirationDate: z.string().optional(),
    documentIssueDate: z.string().optional(),
    nationality: z.string().optional(),
    residenceCountryCode: z.string().optional(),
  }),
  model: z.object({
    type: z.enum(["passport"]),
    number: z.string().optional(),
    issueCountry: z.string().optional(),
    expirationDate: z.date({ coerce: true }).optional(),
    issueDate: z.date({ coerce: true }).optional(),
    nationality: z.string().optional(),
    residenceCountryCode: z.string().optional(),
  }),
  toModel: (data) => ({
    type: data.documentType,
    number: data.documentNumber,
    expirationDate: data.documentExpirationDate ? new Date(data.documentExpirationDate) : undefined,
    issueCountry: data.documentIssueCountry,
    issueDate: data.documentIssueDate ? new Date(data.documentIssueDate) : undefined,
    nationality: data.nationality,
    residenceCountryCode: data.residenceCountryCode,
  }),
  toSchema: (data) => ({
    documentType: data.type,
    documentNumber: data.number,
    documentExpirationDate: data.expirationDate?.toLocaleDateString("sv-SE"),
    documentIssueCountry: data.issueCountry,
    documentIssueDate: data.issueDate?.toLocaleDateString("sv-SE"),
    nationality: data.nationality,
    residenceCountryCode: data.residenceCountryCode,
  }),
});
export type PassportDocumentModel = Infer<typeof passportDocumentModel>;

export const orderPassengerModel = schemaModel.create({
  schema: z.object({
    firstName: z.string(),
    lastName: z.string(),
    title: passengerTitle,
    gender: passengerGender,
    dateOfBirth: z.string(),
    travelerDocument: passportDocumentModel.schema.nullable().optional(),
  }),
  model: z.object({
    firstName: z.string(),
    lastName: z.string(),
    dateOfBirth: z.date({ coerce: true }),
    gender: passengerGender,
    title: passengerTitle,
    document: passportDocumentModel.model.optional(),
  }),
  toSchema: (data) => ({
    ...data,
    dateOfBirth: data.dateOfBirth.toLocaleDateString("sv-SE"),
    travelerDocument: data.document ? passportDocumentModel.toSchema(data.document) : null,
  }),
  toModel: (data) => ({
    ...data,
    dateOfBirth: new Date(data.dateOfBirth),
    document: data.travelerDocument
      ? passportDocumentModel.toModel(data.travelerDocument)
      : undefined,
  }),
});
export type OrderPassengerModel = Infer<typeof orderPassengerModel>;

export const voucherModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["vouchers"]),
  }),
  model: z.object({ id: z.string() }),
  toSchema: (data) => ({ ...data, type: "vouchers" } as const),
});

export const orderModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.enum(["orders"]),
    attributes: z.object({
      passengers: z.array(orderPassengerModel.schema),
      residenceAddress: addressModel.optional(),
    }),
    relationships: schemaModel.relationships({
      payment: paymentIntentModel.identifier,
      voucher: voucherModel.identifier.optional(),
      journey: journeyModel.identifier,
      bookings: z.array(z.lazy(() => bookingModel.identifier)),
    }),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    id: z.string(),
    passengers: z.array(orderPassengerModel.model),
    paymentId: z.string(),
    journeyId: z.string(),
    journey: journeyModel.model.optional(),
    status: z.enum([
      "unspecified",
      "pending",
      "confirmed",
      "rejected",
      "not-ticketed",
      "error",
      "cancelled",
      "unknown",
    ]),
    bookingIds: z.array(z.string()),
    bookings: z.array(z.lazy(() => bookingModel.model)),
  }),
  toModel: (data) => ({
    id: data.id,
    passengers: data.attributes.passengers.map(orderPassengerModel.toModel),
    bookingIds: data.relationships.bookings.data.map((item) => item.id),
    status: "unknown" as const,
    bookings: [],
    journeyId: data.relationships.journey.data.id,
    journey: undefined,
    paymentId: data.relationships.payment.data.id,
  }),
});
export type OrderModel = Infer<typeof orderModel>;
export type OrderSchema = Infer<typeof orderModel, "schema">;
export type OrderIdentifier = Infer<typeof orderModel, "identifier">;

export const createOrderModel = schemaModel.create({
  schema: z.object({
    type: z.enum(["orders"]),
    attributes: z.object({
      contactDetails: contactDetailsModel.schema,
      passengers: z.array(orderPassengerModel.schema),
    }),
    relationships: schemaModel.relationships({
      payment: paymentIntentModel.identifier,
      voucher: voucherModel.identifier.optional(),
      quote: tripOfferPriceQuoteModel.identifier,
    }),
  }),
  model: z.object({
    priceQuoteId: z.string(),
    paymentId: z.string(),
    passengers: z.array(
      z.object({
        firstName: z.string(),
        lastName: z.string(),
        title: passengerTitle,
        gender: passengerGender,
        dateOfBirth: z.date({ coerce: true }),
        document: passportDocumentModel.model.optional(),
      }),
    ),
    contactDetails: contactDetailsModel.model,
  }),
  toSchema: (data) => ({
    type: "orders" as const,
    relationships: {
      payment: { data: { id: data.paymentId, type: "payments" as const } },
      quote: { data: { id: data.priceQuoteId, type: "trip-offer-price-quotes" as const } },
    },
    attributes: {
      contactDetails: contactDetailsModel.toSchema(data.contactDetails),
      passengers: data.passengers.map(orderPassengerModel.toSchema),
    },
  }),
});
export type CreateOrderModel = Infer<typeof createOrderModel>;
export type CreateOrderSchema = Infer<typeof createOrderModel, "schema">;

export const orderMarkupsModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.enum(["markups"]),
    attributes: z.object({
      servicefee: priceModel.schema,
      agencyMarkup: priceModel.schema,
      totalToCollect: priceModel.schema,
    }),
    relationships: schemaModel.relationships({
      order: orderModel.identifier,
    }),
    // TODO: check if this will be implemented
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    id: z.string(),
    servicefee: priceModel.model,
    agencyMarkup: priceModel.model,
    totalToCollect: priceModel.model,
    orderId: z.string(),
  }),
  toModel: (data) => ({
    id: data.id,
    servicefee: priceModel.toModel(data.attributes.servicefee),
    agencyMarkup: priceModel.toModel(data.attributes.agencyMarkup),
    totalToCollect: priceModel.toModel(data.attributes.totalToCollect),
    orderId: data.relationships.order.data.id,
  }),
});
export type OrderMarkupsModel = Infer<typeof orderMarkupsModel>;
export type OrderMarkupsSchema = Infer<typeof orderMarkupsModel, "schema">;
export type OrderMarkupsIdentifier = Infer<typeof orderMarkupsModel, "identifier">;

export const createOrderMarkupsModel = schemaModel.create({
  schema: z.object({
    type: z.enum(["markups"]),
    attributes: z.object({
      servicefee: priceModel.schema,
      agencyMarkup: priceModel.schema,
      totalToCollect: priceModel.schema,
    }),
    relationships: schemaModel.relationships({
      order: orderModel.identifier,
    }),
  }),
  model: z.object({
    servicefee: priceModel.model,
    agencyMarkup: priceModel.model,
    totalToCollect: priceModel.model,
    orderId: z.string(),
  }),
  toSchema: (data) => ({
    type: "markups" as const,
    attributes: {
      servicefee: priceModel.toSchema(data.servicefee),
      agencyMarkup: priceModel.toSchema(data.agencyMarkup),
      totalToCollect: priceModel.toSchema(data.totalToCollect),
    },
    relationships: {
      order: { data: { id: data.orderId, type: "orders" as const } },
    },
  }),
});
export type CreateOrderMarkupsModel = Infer<typeof createOrderModel>;
export type CreateOrderMarkupsSchema = Infer<typeof createOrderModel, "schema">;

export type OrderIncludes =
  | JourneySchema
  | BookingSchema
  | BookingDetailsSchema
  | CabinClassSchema
  | LegTypeSchema;
