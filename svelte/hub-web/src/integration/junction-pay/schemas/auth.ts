import { getSchemaModel, type Infer } from "integration/common/schema-model.server";
import { z } from "zod";

export const userTokenModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["user-tokens"]),
    attributes: z.object({
      token: z.string(),
    }),
  }),
  z.object({
    id: z.string(),
    token: z.string(),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      token: data.attributes.token,
    }),
  },
);
export type UserTokenSchema = Infer<typeof userTokenModel, "schema">;

export const createUserTokenModel = getSchemaModel(
  z.object({
    type: z.enum(["user-tokens"]),
    attributes: z.object({
      email: z.string().email(),
      password: z.string(),
    }),
  }),
  z.object({ email: z.string().email(), password: z.string() }),
  {
    toSchema: (data) => ({
      type: "user-tokens" as const,
      attributes: {
        email: data.email,
        password: data.password,
      },
    }),
  },
);
export type CreateUserTokenModel = Infer<typeof createUserTokenModel>;
