import { z } from "zod";
import { orderModel } from "./order";
import schemaModel, { type Infer } from "utils/schema-model";

const journeyRelationships: z.ZodType<{
  orders: { data: Infer<typeof orderModel, "identifier">[] };
}> = z.lazy(() => schemaModel.relationships({ orders: z.array(orderModel.identifier) }));

export const journeyModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["journeys"]),
    attributes: z.object({
      reference: z.string(),
      contactDetails: z.object({
        email: z.string(),
        address: z.object({
          addressLines: z.array(z.string()),
          countryCode: z.string(),
          postalCode: z.string(),
          city: z.string(),
        }),
        phoneNumber: z.string(),
      }),
    }),
    relationships: journeyRelationships,
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    reference: z.string(),
    contact: z.object({
      email: z.string(),
      address: z.object({
        addressLines: z.array(z.string()),
        countryCode: z.string(),
        postalCode: z.string(),
        city: z.string(),
      }),
      phoneNumber: z.string(),
    }),
  }),
  toModel: (data) => ({
    reference: data.attributes.reference,
    contact: {
      address: {
        addressLines: data.attributes.contactDetails.address.addressLines.filter(
          (line) => line.length,
        ),
        city: data.attributes.contactDetails.address.city,
        countryCode: data.attributes.contactDetails.address.countryCode,
        postalCode: data.attributes.contactDetails.address.postalCode,
      },
      email: data.attributes.contactDetails.email,
      phoneNumber: data.attributes.contactDetails.phoneNumber,
    },
  }),
});
export type JourneySchema = Infer<typeof journeyModel, "schema">;
