export type LoyaltyCard = {
  airlineIata: string;
  number: string;
  firstName: string;
  lastName: string;
};

export type LoyaltyCardSchema = {
  airlineIata: string;
  number: string;
  firstName: string;
  lastName: string;
};

export const loyaltyCardParser = {
  toModel: (data: LoyaltyCardSchema): LoyaltyCard => ({ ...data }),
  toSchema: (data: LoyaltyCard): LoyaltyCardSchema => ({ ...data }),
};
