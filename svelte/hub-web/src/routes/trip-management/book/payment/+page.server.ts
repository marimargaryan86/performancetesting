import { fail, type ActionFailure } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import { getPassengerValidator } from "./passenger-entry.svelte";
import { contactInformationData } from "./contact-information.svelte";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { ensureDefined } from "utils/array";
import type { CreateOrderModel, OrderModel } from "integration/junction-mobile-api/schemas/order";
import bookingManager, { type SearchDataModel } from "../booking-manager.server";
import { z } from "zod";
import { getActionRequestJsonData } from "utils/common";

export type ActionPollReturnType = {
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent: SearchDataModel["paymentIntent"];
};

function getBookingDataModel(required: TripOfferPriceQuoteModel["required"]): z.ZodObject<{
  priceQuoteId: z.ZodString;
  contact: typeof contactInformationData;
  passengers: z.ZodArray<ReturnType<typeof getPassengerValidator>>;
  price: typeof priceModel.model;
}> {
  return z.object({
    priceQuoteId: z.string().uuid(),
    contact: contactInformationData,
    passengers: z.array(getPassengerValidator(required)),
    price: priceModel.model,
  });
}

type BookingData = z.infer<ReturnType<typeof getBookingDataModel>>;

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
    passengers: data.passengers,
    paymentId,
    priceQuoteId: data.priceQuoteId,
  });
}

export async function load(event): Promise<{
  searchData: Pick<SearchDataModel, "passengers">;
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent?: SearchDataModel["paymentIntent"];
}> {
  const searchData = bookingManager.getSearchData(event);
  const result = await actions.poll(event);

  if ("priceQuote" in result) {
    return {
      searchData: {
        passengers: searchData.passengers,
      },
      ...result,
    };
  }

  throw bookingManager.rootRedirect(event);
}

export const actions = {
  async poll(event): Promise<ActionPollReturnType | ActionFailure> {
    try {
      const searchData = bookingManager.getSearchData(event);
      const { priceQuote, paymentIntent } = await bookingManager.getPaymentIntent(
        searchData,
        event,
      );

      bookingManager.setSearchData(
        {
          ...searchData,
          expiresAt: priceQuote.expiresAt,
          priceQuoteId: priceQuote.id,
          paymentIntent,
        },
        event,
      );

      return { priceQuote, paymentIntent };
    } catch {
      return fail(400);
    }
  },
  async createOrder(
    event,
  ): Promise<ActionFailure<{ error: z.ZodFormattedError<CreateOrderModel> }> | void> {
    const searchData = bookingManager.getSearchData(event);
    const { priceQuote, paymentIntent } = await bookingManager.getPaymentIntent(searchData, event);

    try {
      if (!paymentIntent) {
        throw new Error("Payment intent missing");
      }

      const bookingData = await getActionRequestJsonData(
        event,
        getBookingDataModel(priceQuote.required),
      );

      try {
        const order = await createOrder(bookingData, paymentIntent.id);

        bookingManager.setSearchData({ ...searchData, orderId: order.id }, event);
      } catch (err) {
        if (err instanceof z.ZodError) {
          return fail(400, { error: err.format() });
        }

        throw err;
      }
    } catch {
      return fail(400);
    }
  },
  confirmPayment(event): void {
    const searchData = bookingManager.getSearchData(event);

    if (!searchData?.paymentIntent) {
      return;
    }

    bookingManager.setSearchData(
      { ...searchData, paymentIntent: { ...searchData.paymentIntent, confirmed: true } },
      event,
    );
  },
};
