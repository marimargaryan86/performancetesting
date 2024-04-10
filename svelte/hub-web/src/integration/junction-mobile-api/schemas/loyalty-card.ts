import type { TripOfferSearchSchema } from ".";

export type LoyaltyCard = {
  airlineIata: string;
  number: string;
  firstName: string;
  lastName: string;
};

export type LoyaltyCardSchema = NonNullable<TripOfferSearchSchema["attributes"]["loyalty"]>;

export const loyaltyCardParser = {
  toModel: (data: LoyaltyCardSchema): LoyaltyCard => ({ ...data }),
  toSchema: (data: LoyaltyCard): LoyaltyCardSchema => ({ ...data }),
};
