export interface PaymentIntentModel {
  id: string;
  clientSecret: string;
  ephemeralKey?: string;
  customerId?: string;
}
