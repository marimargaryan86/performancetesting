import type { CoordinatesModel } from "models/booking/location";

export interface CreateTripCandidatesModel {
  criteria: {
    origin: CoordinatesModel;
    destination: CoordinatesModel;
    departureAfter: Date;
  }[];
  passengers: { dateOfBirth: Date }[];
  allowedLegTypeIds?: string[];
}
