export type BookingSearchForm = {
  adults: number;
  children: number;
  infants: number;
  origin: string;
  destination: string;
  fromDate: Date | undefined;
  toDate?: Date | undefined;
};
