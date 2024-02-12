import { z } from "zod";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

export const contactDetailsModel: z.ZodType<MobileSchemas.ContactDetails> = z.object({
  email: z.string().email().trim(),
  address: z.object({
    street: z.object({
      line1: z.string().trim().min(1),
      line2: z
        .union([z.string().trim().length(0), z.string().trim().min(1)])
        .optional()
        .transform((val) => (val?.length ? val : undefined)),
    }),
    countryCode: z.string().trim().min(1),
    postalCode: z.string().trim().min(1),
    city: z.string().trim().min(1),
  }),
  phone: z.string().trim().min(1),
});
