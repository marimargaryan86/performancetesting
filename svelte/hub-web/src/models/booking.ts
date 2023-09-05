import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { OrderModel } from "./order";
import type { offerSegmentLegModel } from "integration/junction-mobile-api/schemas/offer";
import type { priceModel } from "integration/junction-mobile-api/schemas/price";

export interface BookingDetailsModel {
  cabinClass: string;
  vendor: string;
  operator?: string;
  routeIdentifiers: {
    vendor: string;
    operator?: string;
  };
  legs: Infer<typeof offerSegmentLegModel>[];
  legType?: string;
}

export interface BookingModel {
  id: string;
  price: Infer<typeof priceModel>;
  operatorReferences: string[];
  externalReference?: string;
  order?: OrderModel;
  status: string;
  details?: BookingDetailsModel;
}
