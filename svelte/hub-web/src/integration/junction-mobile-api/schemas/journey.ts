import { contactDetailsModel, orderModel } from "./order";
import { getSchemaModel, links, relationship, type Infer } from "../schema-model.server";
import { z } from "zod";

const journeyRelationships: z.ZodType<{
  orders: { data: Infer<typeof orderModel, "identifier">[] };
}> = relationship({
  orders: z.array(z.lazy(() => orderModel.schema.pick({ id: true, type: true }))),
});

const journeyModelBase = z.object({
  id: z.string(),
  reference: z.string(),
  contact: z.lazy(() => contactDetailsModel.model),
});

const journeyModelExt: z.ZodType<
  z.infer<typeof journeyModelBase> & { orders: Infer<typeof orderModel>[] }
> = journeyModelBase.extend({
  orders: z.array(z.lazy(() => orderModel.model)),
});

export const journeyModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["journeys"]),
    attributes: z.object({
      reference: z.string(),
      contactDetails: z.lazy(() => contactDetailsModel.schema),
    }),
    relationships: journeyRelationships,
    links: links(["self"]),
  }),
  journeyModelExt,
  {
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
  },
);
