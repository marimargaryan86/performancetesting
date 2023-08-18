import type { JourneyModel } from "models/order";
import type { JourneySchema } from "../schemas/journey";

export function parseJourneySchema(data: JourneySchema): JourneyModel {
  throw new Error(`Not implemented ${data}`);
}
