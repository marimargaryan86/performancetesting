import type { CoordinatesModel, PriceModel } from "$lib/models/common";
import type {
  NameTitle,
  Gender,
  ContactDetailsModel,
  OrderDetailedModel,
  OrderItemBase,
  OrderItemModel,
  OrderItemStatus,
  OrderItemType,
  OrderModel,
  OrderStatus,
  PassengerModel,
  SegmentModel,
  TripModel,
} from "$lib/models/order";
import type { CuratedPlaceModel, PlaceModel } from "$lib/models/place";
import type { ResellerModel } from "$lib/models/reseller";
import type { ProviderModel } from "$lib/models/provider";
import faker from "@faker-js/faker";

function generateCoordinates(): CoordinatesModel {
  return {
    longitude: parseFloat(faker.address.longitude()),
    latitude: parseFloat(faker.address.latitude()),
  };
}

function generatePlace(): PlaceModel {
  return {
    id: faker.datatype.uuid(),
    coordinates: generateCoordinates(),
    countryCode: faker.address.countryCode(),
    name: faker.address.streetName(),
    sourceRef: faker.datatype.uuid(),
    timeZone: faker.address.timeZone(),
    updatedAt: faker.date.past(),
  };
}

function generateCuratedPlace(): CuratedPlaceModel {
  return {
    ...generatePlace(),
    mergedPlaces: [...Array(faker.datatype.number({ min: 1, max: 13 }))].map(() => generatePlace()),
  };
}

function generateReseller(): ResellerModel {
  return {
    id: faker.datatype.uuid(),
    name: faker.company.companyName(),
    orderCount: faker.datatype.number({ min: 3, max: 400 }),
  };
}

function generateProvider(): ProviderModel {
  return {
    id: faker.datatype.uuid(),
    name: faker.company.companyName(),
    orderCount: faker.datatype.number({ min: 4, max: 400 }),
  };
}

function generatePrice(): PriceModel {
  return {
    total: faker.datatype.number({ min: 100, max: 3000, precision: 0.01 }),
    currency: faker.finance.currencyCode(),
  };
}

function generateContactDetails(): ContactDetailsModel {
  return {
    address: faker.address.streetAddress(),
    email: faker.internet.email(),
    phone: faker.phone.phoneNumber(),
  };
}

function generatePassenger(): PassengerModel {
  return {
    dateOfBirth: faker.date.past(),
    firstName: faker.name.firstName(),
    lastName: faker.name.lastName(),
    gender: faker.helpers.arrayElement<Gender>([
      "GENDER_FEMALE",
      "GENDER_MALE",
      "GENDER_UNSPECIFIED",
    ]),
    title: faker.helpers.arrayElement<NameTitle>(["TITLE_UNSPECIFIED"]),
  };
}

function generateOrder(): OrderModel {
  return {
    id: faker.datatype.uuid(),
    spnr: `${faker.random.alpha({ count: 3, upcase: true })}${faker.random
      .alphaNumeric(6)
      .toUpperCase()}`,
    createdAt: faker.date.past(),
    modifiedAt: faker.date.past(),
    reseller: generateReseller(),
    status: faker.helpers.arrayElement<OrderStatus>(["completed", "awaiting-payment", "pending"]),
    itemIds: [...Array(faker.datatype.number({ min: 1, max: 5 }))].map(() => faker.datatype.uuid()),
    price: generatePrice(),
    contactDetails: generateContactDetails(),
    passengers: [...Array(faker.datatype.number({ min: 1, max: 5 }))].map(() =>
      generatePassenger(),
    ),
  };
}

function generateOrderDetailed(): OrderDetailedModel {
  const { itemIds, ...order } = generateOrder();

  return { ...order, items: itemIds.map((id) => ({ ...generateOrderItem(), id })) };
}

function generateSegment(): SegmentModel {
  return {
    origin: generateCuratedPlace(),
    destination: generateCuratedPlace(),
    departureAt: faker.date.future(),
    arrivalAt: faker.date.future(),
  };
}

function generateTrip(): TripModel {
  return {
    id: faker.datatype.uuid(),
    operator: faker.company.companyName(),
    arrivalAt: faker.date.future(),
    departureAt: faker.date.future(),
    destination: generateCuratedPlace(),
    origin: generateCuratedPlace(),
    segments: [...Array(faker.datatype.number({ min: 1, max: 4 }))].map(() => generateSegment()),
  };
}

function generateOrderItem(): OrderItemModel {
  const base: OrderItemBase = {
    id: faker.datatype.uuid(),
    type: faker.helpers.arrayElement<OrderItemType>(["air", "rail"]),
    status: faker.helpers.arrayElement<OrderItemStatus>([
      "awaiting-payment",
      "completed",
      "failed",
      "pending",
    ]),
    provider: generateProvider(),
    price: generatePrice(),
  };

  switch (base.type) {
    case "air":
      return {
        ...base,
        type: "air",
        trips: [...Array(faker.datatype.number({ min: 1, max: 3 }))].map(() => generateTrip()),
      };
    case "rail": {
      return {
        ...base,
        type: "rail",
        trips: [...Array(faker.datatype.number({ min: 1, max: 3 }))].map(() => generateTrip()),
      };
    }
    default:
      throw new Error("Unknown order item type");
  }
}

export default {
  generateOrder,
  generateOrderDetailed,
  generateOrderItem,
  generatePrice,
  generateProvider,
  generateReseller,
  generatePlace,
  generateCuratedPlace,
  generateSegment,
};
