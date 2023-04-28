import type { MoneyModel } from "./money";
import type { OrderModel } from "./order";
import type { PointModel } from "./spatial";

export interface LegModel {
  origin: PointModel;
  destination: PointModel;
  departureAt: Date;
  arrivalAt: Date;
}

export interface BookingDetailsModel {
  cabinClass: string;
  vendor: string;
  operator?: string;
  routeIdentifiers: {
    vendor: string;
    operator?: string;
  };
  legs: LegModel[];
  legType?: string;
}

export interface BookingModel {
  id: string;
  price: MoneyModel;
  operatorReferences: string[];
  externalReference?: string;
  order?: OrderModel;
  status: string;
  details?: BookingDetailsModel;
}
