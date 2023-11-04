import { z } from "zod";

export const resourceStatus = z.enum([
  "unspecified",
  "pending",
  "processing",
  "completed",
  "failed",
]);

export type ResourceStatus = z.infer<typeof resourceStatus>;
