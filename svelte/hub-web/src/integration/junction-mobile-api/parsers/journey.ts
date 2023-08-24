import type { JourneyModel, OrderModel } from "models/booking/order";
import type { JourneySchema } from "../schemas/journey";

export function parseJourneySchema(data: JourneySchema, orders: OrderModel[]): JourneyModel {
  const contactDetails = data.attributes.contactDetails;
  const address = contactDetails.address;
  const orderIds = data.relationships.orders.data.map((item) => item.id);
  const nextOrders = orders.filter((item) => orderIds.includes(item.id));

  return {
    id: data.id,
    reference: data.attributes.reference,
    contact: {
      address: {
        addressLines: address.addressLines,
        city: address.city,
        countryCode: address.countryCode,
        postalCode: address.postalCode,
      },
      email: contactDetails.email,
      phoneNumber: contactDetails.phoneNumber,
    },
    orders: nextOrders,
  };
}
