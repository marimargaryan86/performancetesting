import type { TripCandidatesSearchStatus } from "integration/junction-mobile-api/schemas/trip";
import type { CoordinatesModel } from "./location";

export interface TripCandidatesModel {
  id: string;
  expiresAt: Date;
  status: TripCandidatesSearchStatus;
  criteria: {
    origin: CoordinatesModel;
    destination: CoordinatesModel;
    departureAfter: Date;
  }[];
  passengers: { dateOfBirth: Date }[];
  allowedLegTypeIds?: string[];
}
