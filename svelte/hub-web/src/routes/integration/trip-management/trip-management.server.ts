import type { RequestEvent } from "@sveltejs/kit";
import { getRandomAlphaNumericString } from "utils/random";
import utils from "./utils.server";
import type { Session } from "integration/ory/schemas/authentication";
import type { BookingSessionModel } from "./trip-management";
import integrationInstances from "integration-instances";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";
import { getMinDate } from "utils/date-time";
import { PASSENGER_DEFINITIONS } from "../../trip-management/components/trip-search/passenger-picker/passenger-picker.svelte";
import type { ResourceStatus } from "integration/common/schemas/resource";
import type { Offer } from "integration/junction-mobile-api/schemas/offer";

function getBirthDate(age: number): Date {
  const result = new Date();
  result.setFullYear(result.getFullYear() - age);

  return result;
}

function parsePassengers(
  passengers: NonNullable<BookingSessionModel["searchData"]>["passengers"],
): TripCandidateSearchCreate["passengers"] {
  const parsedDates = Object.fromEntries(
    Object.entries(PASSENGER_DEFINITIONS).map(([key, val]) => [key, getBirthDate(val.span.from)]),
  );

  return Object.entries(passengers).flatMap(([key, count]) =>
    Array(count).fill({ birthDate: parsedDates[key] }),
  );
}

async function getOfferSearch(
  session: Session,
  {
    searchData,
    offerSearch,
    sessionToken,
  }: Pick<BookingSessionModel, "searchData" | "offerSearch" | "sessionToken">,
): Promise<NonNullable<BookingSessionModel["offerSearch"]>> {
  if (!(searchData && sessionToken)) {
    throw new Error("Missing data");
  }

  if (offerSearch && offerSearch.expiresAt > new Date()) {
    try {
      const result = await integrationInstances.junctionMobileApi.simpleOfferSearches.get({
        id: offerSearch.id,
        session,
      });

      return { id: result.id, expiresAt: result.expiresAt, status: result.status };
    } catch {
      //
    }
  }

  const departureAfter = new Date(searchData.outbound);
  departureAfter.setMinutes(departureAfter.getMinutes() - searchData.timeZoneOffset);

  const result = await integrationInstances.junctionMobileApi.simpleOfferSearches.create({
    session,
    data: {
      sessionToken,
      passengers: parsePassengers(searchData.passengers),
      allowedSegmentTypes: ["rail"],
      criteria: { ...searchData, departureAfter },
    },
  });

  return { id: result.id, expiresAt: result.expiresAt, status: result.status };
}

export async function getOffers(
  event: RequestEvent,
): Promise<{ data: Offer[]; status: ResourceStatus }> {
  const { session } = event.locals;
  const bookingSession = utils.getBookingSession(event);
  const sessionToken = bookingSession.sessionToken ?? getRandomAlphaNumericString(32);
  const offerSearch = await getOfferSearch(session, {
    searchData: bookingSession.searchData,
    sessionToken,
    offerSearch: bookingSession.offerSearch,
  });
  const { data: offers } =
    await integrationInstances.junctionMobileApi.simpleOfferSearches.findOffers({
      session,
      simpleOfferSearchId: offerSearch.id,
    });

  utils.setBookingSession(
    {
      ...bookingSession,
      offers: offers.length
        ? { expiresAt: getMinDate(...offers.map((item) => item.expiresAt)) }
        : undefined,
      offerSearch,
      sessionToken,
    },
    event,
  );

  return { status: offerSearch.status, data: offers };
}
