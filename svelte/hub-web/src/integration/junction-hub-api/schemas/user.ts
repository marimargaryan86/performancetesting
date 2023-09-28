import { getSchemaModel } from "integration/common/schema-model.server";
import { z } from "zod";

export const userJwtModel = getSchemaModel(
  z.object({
    custom: z.record(z.unknown()),
    exp: z.number(),
    jti: z.string(),
    // eslint-disable-next-line camelcase
    user_info: z.object({
      id: z.string(),
      email: z.string(),
      metadata: z.record(z.unknown()),
    }),
    version: z.string(),
  }),
  z.object({
    id: z.string(),
    email: z.string(),
    expiresAt: z.date(),
  }),
  {
    toModel: (data) => ({
      id: data.user_info.id,
      email: data.user_info.email,
      expiresAt: new Date(data.exp * 1000),
    }),
  },
);
