import { cabinClassModel, legTypeModel, tripOfferPriceQuoteModel } from "./offer";
import { getSchemaModel, relationship, type Infer, links } from "../schema-model.server";
import { z } from "zod";
import { paymentIntentModel } from "./payment";
import { journeyModel } from "./journey";
import { bookingModel, type bookingDetailsModel } from "./booking";

export const passengerTitle = z.enum(["unspecified", "mr", "mrs", "ms", "miss"]);
export const passengerGender = z.enum(["unspecified", "male", "female"]);

export const addressModel = z.object({
  addressLines: z.array(z.string()),
  countryCode: z.string(),
  postalCode: z.string(),
  city: z.string(),
});

export const contactDetailsModel = getSchemaModel(
  z.object({
    email: z.string().email(),
    address: addressModel,
    phoneNumber: z.string(),
  }),
  z.object({
    address: addressModel,
    email: z.string().email(),
    phone: z.object({
      countryCode: z.string(),
      number: z.string(),
    }),
  }),
  {
    toModel: (data) => ({ ...data, phone: { countryCode: "", number: data.phoneNumber } }),
    toSchema: (data) => ({ ...data, phoneNumber: `${data.phone.countryCode}${data.phone.number}` }),
  },
);

export const passportDocumentModel = getSchemaModel(
  z.object({
    documentType: z.enum(["passport"]),
    documentNumber: z.string().optional(),
    documentIssueCountry: z.string().optional(),
    documentExpirationDate: z.string().optional(),
    documentIssueDate: z.string().optional(),
    nationality: z.string().optional(),
    residenceCountryCode: z.string().optional(),
  }),
  z.object({
    type: z.enum(["passport"]),
    number: z.string().optional(),
  }),
  {
    toModel: (data) => ({
      type: data.documentType,
      number: data.documentNumber,
    }),
    toSchema: (data) => ({
      documentType: data.type,
      documentNumber: data.number,
    }),
  },
);

export const orderPassengerModel = getSchemaModel(
  z.object({
    firstName: z.string(),
    lastName: z.string(),
    title: passengerTitle,
    gender: passengerGender,
    dateOfBirth: z.string(),
    travelerDocument: passportDocumentModel.schema.nullable().optional(),
  }),
  z.object({
    firstName: z.string(),
    lastName: z.string(),
    dateOfBirth: z.date({ coerce: true }),
    gender: passengerGender,
    title: passengerTitle,
    travelerDocument: passportDocumentModel.model.optional(),
  }),
  {
    toSchema: (data) => ({
      ...data,
      dateOfBirth: data.dateOfBirth.toLocaleDateString("sv-SE"),
      travelerDocument: data.travelerDocument
        ? passportDocumentModel.toSchema(data.travelerDocument)
        : null,
    }),
    toModel: (data) => ({
      ...data,
      dateOfBirth: new Date(data.dateOfBirth),
      travelerDocument: data.travelerDocument
        ? passportDocumentModel.toModel(data.travelerDocument)
        : undefined,
    }),
  },
);

export const voucherModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["vouchers"]),
  }),
  z.object({ id: z.string() }),
  { toSchema: (data) => ({ ...data, type: "vouchers" as const }) },
);

export const orderModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["orders"]),
    attributes: z.object({
      passengers: z.array(orderPassengerModel.schema),
      residenceAddress: addressModel.optional(),
    }),
    relationships: relationship({
      payment: paymentIntentModel.schema.pick({ id: true, type: true }),
      voucher: voucherModel.schema.pick({ id: true, type: true }).optional(),
      journey: journeyModel.schema.pick({ id: true, type: true }),
      bookings: z.array(z.lazy(() => bookingModel.schema.pick({ id: true, type: true }))),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    passengers: z.array(orderPassengerModel.model),
    paymentId: z.string(),
    journeyId: z.string(),
    journey: journeyModel.model.optional(),
    bookingIds: z.array(z.string()),
    bookings: z.array(z.lazy(() => bookingModel.model)),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      passengers: data.attributes.passengers.map(orderPassengerModel.toModel),
      bookingIds: data.relationships.bookings.data.map((item) => item.id),
      bookings: [],
      journeyId: data.relationships.journey.data.id,
      journey: undefined,
      paymentId: data.relationships.payment.data.id,
    }),
  },
);

export const createOrderModel = getSchemaModel(
  z.object({
    type: z.enum(["orders"]),
    attributes: z.object({
      contactDetails: contactDetailsModel.schema,
      passengers: z.array(orderPassengerModel.schema),
    }),
    relationships: relationship({
      payment: paymentIntentModel.schema.pick({ id: true, type: true }),
      voucher: voucherModel.schema.pick({ id: true, type: true }).optional(),
      quote: tripOfferPriceQuoteModel.schema.pick({ id: true, type: true }),
    }),
  }),
  z.object({
    priceQuoteId: z.string(),
    paymentId: z.string(),
    passengers: z.array(
      z.object({
        firstName: z.string(),
        lastName: z.string(),
        title: passengerTitle,
        gender: passengerGender,
        dateOfBirth: z.date({ coerce: true }),
        travelerDocument: passportDocumentModel.model.optional(),
      }),
    ),
    contactDetails: contactDetailsModel.model,
  }),
  {
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
  },
);

export type OrderIncludes = (
  | Infer<typeof journeyModel, "schema">
  | Infer<typeof bookingModel, "schema">
  | Infer<typeof bookingDetailsModel, "schema">
  | Infer<typeof cabinClassModel, "schema">
  | Infer<typeof legTypeModel, "schema">
)[];
