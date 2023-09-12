import { getSchemaModel, links, type Infer } from "integration/common/schema-model.server";
import { z } from "zod";

export const cabinClassModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["cabin-classes"]),
    attributes: z.object({ name: z.string() }),
    links: links(["self"]),
  }),
  z.string(),
  { toModel: (data) => data.attributes.name },
);
export type CabinClassSchema = Infer<typeof cabinClassModel, "schema">;

export const legTypeModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["leg-types"]),
    attributes: z.object({ name: z.string() }),
    links: links(["self"]),
  }),
  z.string(),
  { toModel: (data) => data.attributes.name },
);
export type LegTypeSchema = Infer<typeof legTypeModel, "schema">;

export const tripOfferPriceQuoteIdentifier = z.object({
  id: z.string(),
  type: z.enum(["trip-offer-price-quotes"]),
});
