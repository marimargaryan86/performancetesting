import { faker } from "@faker-js/faker";

export default [...Array(6)].map(() => ({
  id: faker.datatype.uuid(),
  name: faker.company.companyName(),
  ref: `${faker.random.numeric(6)}-${faker.random.numeric(5)}`,
  USD: faker.datatype.number({ min: 0, max: 3000 }),
  GBP: faker.datatype.number({ min: 0, max: 3000 }),
  EUR: faker.datatype.number({ min: 0, max: 3000 }),
  AED: faker.datatype.number({ min: 0, max: 3000 }),
  AUD: faker.datatype.number({ min: 0, max: 3000 }),
}));
