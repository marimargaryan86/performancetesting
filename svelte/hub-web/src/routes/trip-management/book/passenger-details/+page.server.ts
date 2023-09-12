import { ActionFailure, fail, redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import { getSearchData, setSearchData, type ResolvedSearchData } from "../common";
import type { ContactInformationData } from "./contact-information.svelte";
import type { PassengerData } from "./passenger-entry.svelte";
import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import type { CreateOrderModel, OrderModel } from "integration/junction-mobile-api/schemas/order";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
import { ensureDefined } from "utils/array";
import routeConfig from "routeConfig";

type BookingData = {
  priceQuoteId: string;
  contact: ContactInformationData;
  passengers: PassengerData[];
  price: PriceModel;
};

function getBookingData(formData: FormData): BookingData {
  const jsonData = JSON.parse(formData.get("json")?.toString() ?? "{}");

  return {
    priceQuoteId: jsonData.priceQuoteId,
    contact: jsonData.contact,
    passengers: (jsonData.passengers as PassengerData[]).map<PassengerData>((item) => ({
      ...item,
      dateOfBirth: new Date(item.dateOfBirth),
      document: item.document
        ? {
            ...item.document,
            expirationDate: item.document.expirationDate
              ? new Date(item.document.expirationDate)
              : undefined,
            issueDate: item.document.issueDate ? new Date(item.document.issueDate) : undefined,
          }
        : undefined,
    })),
    price: jsonData.price,
  };
}

function createOrder(data: BookingData, paymentId: string): Promise<OrderModel> {
  return integrationInstances.junctionMobileApi.orders.createOrder({
    contactDetails: {
      address: {
        addressLines: [data.contact.address.line1, data.contact.address.line2].filter(
          ensureDefined,
        ),
        city: data.contact.city,
        countryCode: data.contact.countryCode,
        postalCode: data.contact.postcode,
      },
      email: data.contact.email,
      phone: {
        countryCode: data.contact.phone.code,
        number: data.contact.phone.number,
      },
    },
    passengers: data.passengers.map<CreateOrderModel["passengers"][number]>((item) => ({
      dateOfBirth: new Date(item.dateOfBirth),
      firstName: item.firstName,
      lastName: item.lastName,
      document: item.document,
      title: item.title ?? "unspecified",
      gender: item.gender ?? "unspecified",
    })),
    paymentId,
    priceQuoteId: data.priceQuoteId,
  });
}

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  priceQuote: TripOfferPriceQuoteModel;
}> {
  const searchData = getSearchData(event);

  if (!searchData?.priceQuoteId) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  try {
    const [origin, destination, priceQuote] = await Promise.all([
      integrationInstances.junctionMobileApi.places.getPlace(searchData.originId),
      integrationInstances.junctionMobileApi.places.getPlace(searchData.destinationId),
      integrationInstances.junctionMobileApi.offers.getPriceQuote(searchData.priceQuoteId),
    ]);

    return {
      searchData: {
        sessionToken: searchData.sessionToken,
        origin,
        destination,
        departureAfter: searchData.departureAfter,
        passengers: searchData.passengers,
      },
      priceQuote,
    };
  } catch {
    throw redirect(303, routeConfig.tripManagement.book.root);
  }
}

export const actions = {
  async poll(
    event,
  ): Promise<{ priceQuote: TripOfferPriceQuoteModel } | ActionFailure<{ error: string }>> {
    const searchData = getSearchData(event);

    if (!searchData?.priceQuoteId) {
      return fail(400, { error: "No quote ID found" });
    }

    try {
      return {
        priceQuote: await integrationInstances.junctionMobileApi.offers.getPriceQuote(
          searchData.priceQuoteId,
        ),
      };
    } catch {
      return fail(404, { error: "Quote not found" });
    }
  },
  async createOrder(event): Promise<ActionFailure<{ error: string }> | undefined> {
    const formData = await event.request.formData();
    const searchData = getSearchData(event);
    const bookingData = getBookingData(formData);

    if (!searchData) {
      return fail(400, { error: "No search data found" });
    }

    if (!searchData.priceQuoteId) {
      return fail(400, { error: "No quote ID found" });
    }

    if (!searchData.paymentIntent) {
      return fail(400, { error: "No payment intent found" });
    }

    try {
      const order = await createOrder(bookingData, searchData.paymentIntent.id);

      setSearchData({ ...searchData, orderId: order.id }, event);
    } catch {
      return fail(400, { error: "Failed to create booking" });
    }

    return undefined;
  },
};
