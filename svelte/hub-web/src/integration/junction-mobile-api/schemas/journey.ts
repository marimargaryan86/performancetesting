import schemaModel, { type Infer } from "utils/schema-model";
import { contactDetailsModel, orderModel, type OrderIdentifier, type OrderModel } from "./order";
import { z } from "zod";

const journeyRelationships: z.ZodType<{
  orders: { data: OrderIdentifier[] };
}> = z.lazy(() =>
  schemaModel.relationships({
    orders: z.array(orderModel.identifier),
  }),
);

const journeyModelBase = z.object({
  id: z.string(),
  reference: z.string(),
  contact: z.lazy(() => contactDetailsModel.model),
});

const journeyModelExt: z.ZodType<z.infer<typeof journeyModelBase> & { orders: OrderModel[] }> =
  z.lazy(() =>
    journeyModelBase.extend({
      orders: z.array(orderModel.model),
    }),
  );

export const journeyModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["journeys"]),
    attributes: z.object({
      reference: z.string(),
      contactDetails: z.lazy(() => contactDetailsModel.schema),
    }),
    relationships: journeyRelationships,
    links: schemaModel.links({ self: true }),
  }),
  model: journeyModelExt,
  toModel: (data): z.infer<typeof journeyModelExt> => {
    const contactDetails = data.attributes.contactDetails;
    const address = contactDetails.address;

    return {
      id: data.id,
      reference: data.attributes.reference,
      contact: {
        address: {
          addressLines: address.addressLines,
          city: address.city,
          countryCode: address.countryCode,
          postalCode: address.postalCode,
        },
        email: contactDetails.email,
        phone: { countryCode: "", number: contactDetails.phoneNumber },
      },
      orders: [],
    };
  },
});
export type JourneyModel = Infer<typeof journeyModel>;
export type JourneySchema = Infer<typeof journeyModel, "schema">;
