import {
  relationship,
  type Infer,
  getSchemaModel,
  links,
} from "integration/common/schema-model.server";
import { z } from "zod";
import { bookingModel } from "./booking";

export const cancellationRequestModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["cancellation-request"]),
    attributes: z.object({
      status: z.enum(["unspecified", "pending", "completed"]),
    }),
    relationships: relationship({
      bookings: z.array(bookingModel.identifier),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string().uuid(),
    status: z.enum(["unspecified", "pending", "completed"]),
    bookingIds: z.array(z.string().uuid()),
    bookings: z.array(bookingModel.model),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      bookingIds: data.relationships.bookings.data.map((item) => item.id),
      status: data.attributes.status,
      bookings: [],
    }),
  },
);
export type CancellationRequestModel = Infer<typeof cancellationRequestModel>;
export type CancellationRequestSchema = Infer<typeof cancellationRequestModel, "schema">;

export const createCancellationRequestModel = getSchemaModel(
  cancellationRequestModel.schema.pick({ type: true, relationships: true }),
  cancellationRequestModel.model.pick({ bookingIds: true }),
  {
    toSchema: (data) => ({
      type: "cancellation-request" as const,
      relationships: {
        bookings: { data: data.bookingIds.map((id) => ({ id, type: "trip-bookings" as const })) },
      },
    }),
  },
);
export type CreateCancellationRequestModel = Infer<typeof createCancellationRequestModel>;
