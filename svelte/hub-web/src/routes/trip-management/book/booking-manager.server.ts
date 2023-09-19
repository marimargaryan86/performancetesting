import { redirect, type Redirect, type RequestEvent } from "@sveltejs/kit";
import { z } from "zod";
import jwt from "jsonwebtoken";
import integrationInstances from "integration-instances";
import type { TripCandidatesSearchModel } from "integration/junction-mobile-api/schemas/trip";
import { getRandomAlphaNumericString } from "utils/random";
import type {
  OfferModel,
  TripOfferPriceQuoteModel,
} from "integration/junction-mobile-api/schemas/offer";
import { paymentIntentModel } from "integration/junction-mobile-api/schemas/payment";
import routeConfig from "routeConfig";

const SEARCH_TOKEN = "search-token";
const JWT_SECRET = "jwt-secret";
const COOKIE_OPTIONS = { path: "/", httpOnly: true, sameSite: "strict" as const };

export type PassengerCountData = {
  adults: number;
  children: number;
  infants: number;
};

const searchDataModel = z.object({
  origin: z.object({
    id: z.string().uuid(),
    lat: z.number(),
    lon: z.number(),
  }),
  destination: z.object({
    id: z.string().uuid(),
    lat: z.number(),
    lon: z.number(),
  }),
  outbound: z.date({ coerce: true }),
  passengers: z.object({
    adults: z.number(),
    children: z.number(),
    infants: z.number(),
  }),
  tripCandidatesId: z.string().uuid().optional(),
  priceQuoteId: z.string().uuid().optional(),
  offerId: z.string().uuid().optional(),
  optionIds: z.array(z.string().uuid()).optional(),
  sessionToken: z.string().optional(),
  expiresAt: z.date({ coerce: true }).optional(),
  paymentIntent: paymentIntentModel.model.extend({ confirmed: z.boolean().optional() }).optional(),
  orderId: z.string().uuid().optional(),
});
export type SearchDataModel = z.infer<typeof searchDataModel>;

function rootRedirect(event: RequestEvent): Redirect {
  deleteSearchData(event);

  return redirect(303, routeConfig.tripManagement.book.root);
}

function parsePassengers(passengersCount: SearchDataModel["passengers"]): { dateOfBirth: Date }[] {
  const adult = new Date();
  adult.setFullYear(adult.getFullYear() - 25);
  const child = new Date();
  child.setFullYear(child.getFullYear() - 7);
  const infant = new Date();
  infant.setFullYear(infant.getFullYear() - 1);

  return [
    ...Array(passengersCount.adults).fill({ dateOfBirth: adult }),
    ...Array(passengersCount.children).fill({ dateOfBirth: child }),
    ...Array(passengersCount.infants).fill({ dateOfBirth: infant }),
  ];
}

function getSearchData(event: RequestEvent): SearchDataModel {
  try {
    const token = event.cookies.get(SEARCH_TOKEN);

    if (!token) {
      throw new Error();
    }

    return searchDataModel.parse(jwt.decode(token));
  } catch (err) {
    throw rootRedirect(event);
  }
}

function setSearchData(data: SearchDataModel, event: RequestEvent): void {
  const parsedResult = searchDataModel.safeParse(data);

  if (!parsedResult.success) {
    throw new Error("Failed to parse search data", { cause: parsedResult.error });
  }

  const token = jwt.sign(JSON.stringify(parsedResult.data), JWT_SECRET);

  event.cookies.set(SEARCH_TOKEN, token, COOKIE_OPTIONS);
}

function deleteSearchData(event: RequestEvent): void {
  event.cookies.delete(SEARCH_TOKEN, COOKIE_OPTIONS);
}

async function getTripCandidates(data: SearchDataModel): Promise<{
  sessionToken: string;
  tripCandidates: TripCandidatesSearchModel;
}> {
  let tripCandidates: TripCandidatesSearchModel | undefined = undefined;

  if (data.tripCandidatesId) {
    try {
      tripCandidates = await integrationInstances.junctionMobileApi.trips.getTripCandidatesSearch(
        data.tripCandidatesId,
      );
    } catch {
      //
    }
  }

  let sessionToken = data.sessionToken ?? getRandomAlphaNumericString(32);

  if (!tripCandidates) {
    sessionToken = getRandomAlphaNumericString(32);

    tripCandidates = await integrationInstances.junctionMobileApi.trips.createTripCandidatesSearch({
      criteria: [
        {
          departureAfter: data.outbound,
          origin: data.origin,
          destination: data.destination,
        },
      ],
      sessionToken,
      passengers: parsePassengers(data.passengers),
      allowedLegTypeIds: ["rail"],
    });
  }

  return {
    sessionToken,
    tripCandidates,
  };
}

async function getOffers(
  data: SearchDataModel,
  event: RequestEvent,
): Promise<{
  sessionToken: string;
  tripCandidatesId: string;
  expiresAt: Date;
  status: TripCandidatesSearchModel["status"];
  offers: OfferModel[];
}> {
  try {
    const { tripCandidates, sessionToken } = await getTripCandidates(data);
    const offers = await integrationInstances.junctionMobileApi.trips.getTripCandidatesOffers(
      tripCandidates.id,
    );

    if (tripCandidates.expiresAt < new Date()) {
      throw new Error("Trip candidates expired");
    }

    return {
      sessionToken,
      tripCandidatesId: tripCandidates.id,
      expiresAt: tripCandidates.expiresAt,
      status: tripCandidates.status,
      offers,
    };
  } catch {
    throw rootRedirect(event);
  }
}

async function getPriceQuote(
  searchData: SearchDataModel,
  event: RequestEvent,
): Promise<TripOfferPriceQuoteModel> {
  if (searchData.priceQuoteId) {
    try {
      return await integrationInstances.junctionMobileApi.offers.getPriceQuote(
        searchData.priceQuoteId,
      );
    } catch {
      //
    }
  }

  if (!(searchData.sessionToken && searchData.offerId && searchData.optionIds?.length)) {
    throw rootRedirect(event);
  }

  try {
    return integrationInstances.junctionMobileApi.offers.createPriceQuote({
      sessionToken: searchData.sessionToken,
      offerId: searchData.offerId,
      optionIds: searchData.optionIds,
    });
  } catch {
    throw rootRedirect(event);
  }
}

async function getPaymentIntent(
  searchData: SearchDataModel,
  event: RequestEvent,
): Promise<Pick<SearchDataModel, "paymentIntent"> & { priceQuote: TripOfferPriceQuoteModel }> {
  try {
    const priceQuote = await getPriceQuote(searchData, event);

    const paymentIntent =
      !searchData.paymentIntent && priceQuote.price
        ? await integrationInstances.junctionMobileApi.payments.createPayment(priceQuote.price)
        : searchData.paymentIntent;

    return {
      priceQuote,
      paymentIntent,
    };
  } catch {
    throw rootRedirect(event);
  }
}

export default {
  getSearchData,
  setSearchData,
  getOffers,
  getPriceQuote,
  getPaymentIntent,
  rootRedirect,
};
