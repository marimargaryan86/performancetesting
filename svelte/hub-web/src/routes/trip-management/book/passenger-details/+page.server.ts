import { ActionFailure, error, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import { getSearchData, setSearchData, type ResolvedSearchData } from "../common";
import type { ContactInformationData } from "./contact-information.svelte";
import type { PartialPassengerData } from "./passenger-entry.svelte";
import type { tripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { createOrderModel, orderModel } from "integration/junction-mobile-api/schemas/order";
import type { priceModel } from "integration/junction-mobile-api/schemas/price";
import { ensureDefined } from "utils/array";

type BookingData = {
  priceQuoteId: string;
  contact: ContactInformationData;
  passengers: PartialPassengerData[];
  price: Infer<typeof priceModel>;
};

function getBookingData(formData: FormData): BookingData {
  const jsonData = JSON.parse(formData.get("json")?.toString() ?? "{}");

  return {
    priceQuoteId: jsonData.priceQuoteId,
    contact: jsonData.contact,
    passengers: (jsonData.passengers as PartialPassengerData[]).map<PartialPassengerData>(
      (item) => ({
        ...item,
        dateOfBirth: item.dateOfBirth ? new Date(item.dateOfBirth) : undefined,
      }),
    ),
    price: jsonData.price,
  };
}

function createOrder(data: BookingData, paymentId: string): Promise<Infer<typeof orderModel>> {
  return integrationInstances.junctionMobileApi.orders.createOrder({
    contactDetails: {
      address: {
        addressLines: [data.contact.address.line1, data.contact.address.line2].filter(
          ensureDefined,
        ),
        city: data.contact.city ?? "",
        countryCode: data.contact.countryCode ?? "",
        postalCode: data.contact.postcode ?? "",
      },
      email: data.contact.email ?? "",
      phone: {
        countryCode: data.contact.phone.code ?? "",
        number: data.contact.phone.number ?? "",
      },
    },
    passengers: data.passengers.map<Infer<typeof createOrderModel>["passengers"][number]>(
      (item) => ({
        dateOfBirth: item.dateOfBirth ?? new Date(),
        firstName: item.firstName ?? "",
        lastName: item.lastName ?? "",
        travelerDocument:
          item.document.type === "passport"
            ? {
                type: item.document.type,
                number: item.document.number,
              }
            : undefined,
        title: item.title ?? "unspecified",
        gender: item.gender ?? "unspecified",
      }),
    ),
    paymentId,
    priceQuoteId: data.priceQuoteId,
  });
}

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  priceQuote: Infer<typeof tripOfferPriceQuoteModel>;
}> {
  const searchData = getSearchData(event);

  if (!searchData?.priceQuoteId) {
    throw error(400, { message: "No quote ID found" });
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
    throw error(404, { message: "Quote not found" });
  }
}

export const actions = {
  async poll(
    event,
  ): Promise<
    { priceQuote: Infer<typeof tripOfferPriceQuoteModel> } | ActionFailure<{ error: string }>
  > {
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
