import type { IncludedMapping } from "./included";
import { loyaltyCardParser, type LoyaltyCard, type LoyaltyCardSchema } from "./loyalty-card";
import type { Offer, OfferSchema } from "./offer";

export type TripOfferPassenger = {
  birthDate: Date;
};

export type TripOfferPassengerSchema = {
  dateOfBirth: string;
};

export const tripOfferPassengerParser = {
  toModel: (data: TripOfferPassengerSchema): TripOfferPassenger => ({
    birthDate: new Date(data.dateOfBirth),
  }),
  toSchema: (data: TripOfferPassenger): TripOfferPassengerSchema => ({
    dateOfBirth: data.birthDate.toLocaleDateString("sv-SE"),
  }),
};

export type TripOfferSearch = {
  id: string;
  expiresAt: Date;
  passengers: TripOfferPassenger[];
  loyalty?: LoyaltyCard;
  status: "unspecified" | "pending" | "processing" | "completed" | "failed";
  offerIds: string[];
  offers: Offer[];
};

export type TripOfferSearchSchema = {
  id: string;
  type: "trip-offer-searches";
  attributes: {
    expiresAt: string;
    passengers: TripOfferPassengerSchema[];
    loyalty?: LoyaltyCardSchema;
    status: "unspecified" | "pending" | "processing" | "completed" | "failed";
  };
  relationships: {
    offers: { data: Pick<OfferSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export const tripOfferSearchParser = {
  toModel: (data: TripOfferSearchSchema, included?: IncludedMapping): TripOfferSearch => {
    const offerIds = data.relationships.offers.data.map(({ id }) => id);

    return {
      id: data.id,
      expiresAt: new Date(data.attributes.expiresAt),
      passengers: data.attributes.passengers.map(tripOfferPassengerParser.toModel),
      loyalty: data.attributes.loyalty
        ? loyaltyCardParser.toModel(data.attributes.loyalty)
        : undefined,
      status: data.attributes.status,
      offerIds,
      offers: included?.offers?.filter(({ id }) => offerIds.includes(id)) ?? [],
    };
  },
};
