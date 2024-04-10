import type { PostCreatedResponse } from "~/integration/common/types";
import type { Specification } from "./__generated__";
import type { IncludedMapping } from "./included";
import { loyaltyCardParser, type LoyaltyCard } from "./loyalty-card";
import type { Offer } from "./offer";

export type TripOfferPassenger = {
  birthDate: Date;
};

export type TripOfferPassengerSchema = TripOfferSearchSchema["attributes"]["passengers"][number];

export const tripOfferPassengerParser = {
  toModel: (data: TripOfferPassengerSchema): TripOfferPassenger => ({
    birthDate: new Date(data.dateOfBirth),
  }),
  toSchema: (data: TripOfferPassenger): TripOfferPassengerSchema => ({
    dateOfBirth: data.birthDate.toLocaleDateString("sv-SE", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }),
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

export type TripOfferSearchSchema = PostCreatedResponse<Specification, "/offers/searches">["data"];

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
