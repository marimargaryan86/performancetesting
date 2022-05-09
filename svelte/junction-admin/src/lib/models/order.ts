import type { PriceModel } from "./common";
import type { CuratedPlaceModel } from "./place";

export type OrderStatus = "pending" | "awaiting-payment" | "completed";

export type OrderItemStatus = "failed" | "pending" | "awaiting-payment" | "completed";

export type OrderSearchData = {
  spnr?: string;
  reseller?: string;
  status?: OrderStatus;
};

export type ResellerModel = {
  id: string;
  name: string;
};

export type ProviderModel = {
  id: string;
  name: string;
};

export type SegmentModel = {
  origin: CuratedPlaceModel;
  destination: CuratedPlaceModel;
  departureAt: Date;
  arrivalAt: Date;
};

export type TripModel = {
  id: string;
  operator: string;
  origin: CuratedPlaceModel;
  destination: CuratedPlaceModel;
  departureAt: Date;
  arrivalAt: Date;
  segments: SegmentModel[];
};

export type OrderItemType = "rail" | "air";

export type OrderItemBase = {
  id: string;
  type: OrderItemType;
  status: OrderItemStatus;
  provider: ProviderModel;
  price: PriceModel;
};

export type OrderItemRailModel = OrderItemBase & {
  type: "rail";
  trips: TripModel[];
};

export type OrderItemAirModel = OrderItemBase & {
  type: "air";
  trips: TripModel[];
};

export type OrderItemModel = OrderItemRailModel | OrderItemAirModel;

export type ContactDetailsModel = {
  address: string;
  phone: string;
  email: string;
};

export type NameTitle = "TITLE_UNSPECIFIED";

export type Gender = "GENDER_UNSPECIFIED" | "GENDER_MALE" | "GENDER_FEMALE";

export type PassengerModel = {
  firstName: string;
  lastName: string;
  title: NameTitle;
  gender: Gender;
  dateOfBirth: Date;
};

export type OrderModel = {
  id: string;
  spnr: string;
  createdAt: Date;
  modifiedAt: Date;
  reseller: ResellerModel;
  status: OrderStatus;
  itemIds: string[];
  price: PriceModel;
  contactDetails: ContactDetailsModel;
  passengers: PassengerModel[];
};

export type OrderDetailedModel = Omit<OrderModel, "itemIds"> & {
  items: OrderItemModel[];
};
