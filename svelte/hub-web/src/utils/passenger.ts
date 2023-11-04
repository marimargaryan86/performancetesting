import type { OrderPassenger } from "integration/junction-mobile-api/schemas/order";
import { getTimeDeltaMs } from "./date-time";

export function getPassengerType(passenger: OrderPassenger): "adult" | "child" | "infant" {
  const deltaMs = getTimeDeltaMs(new Date(), passenger.birthDate);
  const deltaHours = Math.floor(deltaMs / 3600000);
  const deltaYears = Math.floor(deltaHours / 8760);

  if (deltaYears < 2) {
    return "infant";
  }

  if (deltaYears < 12) {
    return "child";
  }

  return "adult";
}
