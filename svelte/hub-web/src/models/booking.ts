import type { OrderModel } from "./order";
import type { OfferSegmentLegModel } from "integration/junction-mobile-api/schemas/offer";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";

export interface BookingDetailsModel {
  cabinClass: string;
  vendor: string;
  operator?: string;
  routeIdentifiers: {
    vendor: string;
    operator?: string;
  };
  legs: OfferSegmentLegModel[];
  legType?: string;
}

export interface BookingModel {
  id: string;
  price: PriceModel;
  operatorReferences: string[];
  externalReference?: string;
  order?: OrderModel;
  status: string;
  details?: BookingDetailsModel;
}
