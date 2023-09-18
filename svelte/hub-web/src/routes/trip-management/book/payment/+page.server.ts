import { error, fail, redirect, type ActionFailure } from "@sveltejs/kit";
import { getSearchData, setSearchData, type SearchData, type ResolvedSearchData } from "../common";
import integrationInstances from "integration-instances";
import routeConfig from "routeConfig";
import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import type { PaymentIntentModel } from "integration/junction-mobile-api/schemas/payment";
import type { PassengerData } from "./passenger-entry.svelte";
import type { ContactInformationData } from "./contact-information.svelte";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
import { ensureDefined } from "utils/array";
import type { CreateOrderModel, OrderModel } from "integration/junction-mobile-api/schemas/order";

export type ActionPollReturnType = {
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent?: PaymentIntentModel;
};

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

async function getPriceQuoteAndPaymentIntent(searchData: SearchData): Promise<{
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent?: PaymentIntentModel;
}> {
  if (!searchData.priceQuoteId) {
    throw error(400, { message: "No quote ID found" });
  }

  let priceQuote: TripOfferPriceQuoteModel | undefined;

  try {
    priceQuote = await integrationInstances.junctionMobileApi.offers.getPriceQuote(
      searchData.priceQuoteId,
    );
  } catch {
    priceQuote = undefined;
  }

  if (!priceQuote) {
    throw error(404, { message: "Quote not found" });
  }

  let paymentIntent = searchData.paymentIntent;

  if (!paymentIntent && priceQuote.price) {
    try {
      paymentIntent = await integrationInstances.junctionMobileApi.payments.createPayment(
        priceQuote.price,
      );
    } catch {
      throw error(500, { message: "Failed to create payment intent" });
    }
  }

  return { priceQuote, paymentIntent };
}

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  priceQuote: TripOfferPriceQuoteModel;
}> {
  const searchData = getSearchData(event);

  if (!searchData) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  try {
    const [origin, destination, { priceQuote, paymentIntent }] = await Promise.all([
      integrationInstances.junctionMobileApi.places.getPlace(searchData.originId),
      integrationInstances.junctionMobileApi.places.getPlace(searchData.destinationId),
      getPriceQuoteAndPaymentIntent(searchData),
    ]);

    setSearchData({ ...searchData, paymentIntent }, event);

    return {
      searchData: {
        sessionToken: searchData.sessionToken,
        origin,
        destination,
        departureAfter: new Date(searchData.departureAfter),
        passengers: searchData.passengers,
        paymentIntent,
      },
      priceQuote,
    };
  } catch {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }
}

export const actions = {
  async poll(event): Promise<ActionPollReturnType | ActionFailure<{ error: string }>> {
    const searchData = getSearchData(event);

    if (!searchData) {
      throw error(400, { message: "No search data found" });
    }

    try {
      const { priceQuote, paymentIntent } = await getPriceQuoteAndPaymentIntent(searchData);

      setSearchData({ ...searchData, paymentIntent }, event);

      return { priceQuote, paymentIntent };
    } catch (err) {
      const castErr = err as { status: number; body: { message: string } };

      return fail(castErr.status, { error: castErr.body.message });
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
  confirmPayment(event): void {
    const searchData = getSearchData(event);

    if (!searchData?.paymentIntent) {
      return;
    }

    setSearchData(
      { ...searchData, paymentIntent: { ...searchData.paymentIntent, confirmed: true } },
      event,
    );
  },
};
