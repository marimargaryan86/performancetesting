import { bookingModel } from "./booking";
import { journeyModel } from "./journey";
import { tripOfferPriceQuoteIdentifier } from "./offer";
import {
  getSchemaModel,
  relationship,
  type Infer,
  links,
} from "integration/common/schema-model.server";
import { z } from "zod";

export const orderPassengerModel = getSchemaModel(
  z.object({
    firstName: z.string(),
    lastName: z.string(),
    title: z.enum(["unspecified", "mr", "mrs", "ms", "miss"]),
    gender: z.enum(["unspecified", "male", "female"]),
    dateOfBirth: z.string(),
    travelerDocument: z
      .object({
        documentType: z.enum(["passport"]).optional(),
        documentNumber: z.string().optional(),
        documentIssueCountry: z.string().optional(),
        documentExpirationDate: z.string().optional(),
        documentIssueDate: z.string().optional(),
        nationality: z.string().optional(),
        residenceCountryCode: z.string().optional(),
      })
      .optional(),
  }),
  z.object({
    firstName: z.string(),
    lastName: z.string(),
    title: z.enum(["unspecified", "mr", "mrs", "ms", "miss"]),
    gender: z.enum(["unspecified", "male", "female"]),
    dateOfBirth: z.date({ coerce: true }),
    travelerDocument: z
      .object({
        type: z.enum(["passport"]).optional(),
        number: z.string().optional(),
        issueCountry: z.string().optional(),
        expirationDate: z.date({ coerce: true }).optional(),
        issueDate: z.date({ coerce: true }).optional(),
        nationality: z.string().optional(),
        residenceCountryCode: z.string().optional(),
      })
      .optional(),
  }),
  {
    toModel: (data) => ({
      dateOfBirth: new Date(data.dateOfBirth),
      firstName: data.firstName,
      gender: data.gender,
      lastName: data.lastName,
      title: data.title,
      travelerDocument: data.travelerDocument
        ? {
            type: data.travelerDocument.documentType,
            expirationDate: data.travelerDocument.documentExpirationDate
              ? new Date(data.travelerDocument.documentExpirationDate)
              : undefined,
            issueCountry: data.travelerDocument.documentIssueCountry,
            issueDate: data.travelerDocument.documentIssueDate
              ? new Date(data.travelerDocument.documentIssueDate)
              : undefined,
            nationality: data.travelerDocument.nationality,
            number: data.travelerDocument.documentNumber,
            residenceCountryCode: data.travelerDocument.residenceCountryCode,
          }
        : undefined,
    }),
  },
);
export type OrderPassengerModel = Infer<typeof orderPassengerModel>;

const orderRelationships: z.ZodType<{
  quote: { data: z.infer<typeof tripOfferPriceQuoteIdentifier> };
  journey: { data: Infer<typeof journeyModel, "identifier"> };
  bookings: { data: Infer<typeof bookingModel, "identifier"> };
}> = relationship({
  quote: tripOfferPriceQuoteIdentifier,
  journey: z.lazy(() => journeyModel.identifier),
  bookings: z.lazy(() => bookingModel.identifier),
});

const orderBase = z.object({
  passengers: z.array(orderPassengerModel.model),
});

const orderExt: z.ZodType<
  z.infer<typeof orderBase> & {
    journeys: Infer<typeof journeyModel>[];
  }
> = orderBase.extend({
  journeys: z.array(z.lazy(() => journeyModel.model)),
});

export const orderModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["orders"]),
    attributes: z.object({
      passengers: z.array(orderPassengerModel.schema),
    }),
    relationships: orderRelationships,
    links: links(["self"]),
  }),
  orderExt,
  {
    toModel: (data) => ({
      passengers: data.attributes.passengers.map(orderPassengerModel.toModel),
      journeys: [],
    }),
  },
);
export type OrderModel = Infer<typeof orderModel>;
export type OrderSchema = Infer<typeof orderModel, "schema">;
