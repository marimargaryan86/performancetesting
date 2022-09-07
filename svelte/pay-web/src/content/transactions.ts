import { faker } from "@faker-js/faker";

export default [...Array(7)].map(() => ({
  ref: `${faker.random.numeric(8)}-${faker.random.alpha({ count: 6 })}`,
  createdAt: faker.date.past(),
  ...(() => {
    const status = faker.helpers.arrayElement(["Completed", "Pending"]);

    return {
      status,
      completedAt: status === "Completed" ? faker.date.past() : undefined,
    };
  })(),
  type: faker.helpers.arrayElement(["Conversion", "Funding"]),
  ...(() => {
    const code = faker.helpers.arrayElement(["GBP", "SEK", "USD"]);

    return {
      amount: {
        amount: faker.datatype.number({ min: 100, max: 2000 }),
        code,
      },
      balance: {
        amount: faker.datatype.number({ min: 10000, max: 200000 }),
        code,
      },
    };
  })(),
}));
