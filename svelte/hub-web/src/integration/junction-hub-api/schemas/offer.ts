import schemaModel, { type Infer } from "utils/schema-model";
import { z } from "zod";

export const cabinClassModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("cabin-classes"),
    attributes: z.object({ name: z.string() }),
    links: schemaModel.links({ self: true }),
  }),
  model: z.string(),
  toModel: (data) => data.attributes.name,
});
export type CabinClassSchema = Infer<typeof cabinClassModel, "schema">;
export type CabinClassIdentifier = Infer<typeof cabinClassModel, "identifier">;

export const legTypeModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("leg-types"),
    attributes: z.object({ name: z.string() }),
    links: schemaModel.links({ self: true }),
  }),
  model: z.string(),
  toModel: (data) => data.attributes.name,
});
export type LegTypeSchema = Infer<typeof legTypeModel, "schema">;
export type LegTypeIdentifier = Infer<typeof legTypeModel, "identifier">;

export const tripOfferPriceQuoteIdentifier = z.object({
  id: z.string(),
  type: z.literal("trip-offer-price-quotes"),
});
