export type Balance = {
  amount: number;
  code: string;
};

export type Fluctuation = Balance;
export type Price = Balance;

export type Order = {
  ref: string;
  createdAt: Date;
  provider: string;
  price: Price;
  status: "Pending" | "Completed";
};

export type Rate = {
  code: string;
  live: number;
  yesterday: number;
  lastWeek: number;
};

export type Payment = {
  price: Price;
  dueDate: Date;
};
