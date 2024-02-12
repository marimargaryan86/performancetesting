<script lang="ts" context="module">
  import type { TripBooking as MobileTripBooking } from "~/integration/junction-mobile-api/schemas/booking";
  import type { TripBooking as HubTripBooking } from "~/integration/junction-hub-api/schemas/booking";

  type TripBooking = MobileTripBooking | HubTripBooking;

  function getOrigDestLegs(booking: TripBooking):
    | {
        originLeg: OfferSegmentLeg;
        destinationLeg: OfferSegmentLeg;
      }
    | undefined {
    const originLegs = booking.detailsList[0]?.legs;
    const originLeg = originLegs?.[0];
    const destinationLegs = booking.detailsList[booking.detailsList.length - 1]?.legs;
    const destinationLeg = destinationLegs?.[destinationLegs.length - 1];

    if (originLeg && destinationLeg) {
      return { originLeg, destinationLeg };
    }

    return undefined;
  }
</script>

<script lang="ts">
  import { formatDuration } from "$lib/formatting/date-time";
  import { getTimeDeltaS } from "$lib/utils/date-time";
  import EntityAvatar from "$lib/components/ui/entity-avatar.svelte";
  import type { OfferSegmentLeg } from "~/integration/common/schemas/offer-segment-leg";
  import { getLocale, getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";

  export let bookings: TripBooking[];

  const locale = getLocale();
  const t = getTranslator();
</script>

<div class="itinerary">
  <h3 typography="body-large" weight="bold">{$t("words.itineraryDetails")}</h3>

  {#each bookings as booking}
    {@const origDestLegs = getOrigDestLegs(booking)}
    {@const cabinClasses = Array.from(
      new Set(booking.detailsList.map((item) => item.cabinClassName)),
    )}
    {@const vendor = booking.detailsList[0]?.vendor ?? $t("words.unknown")}
    {@const trainNumber = booking.detailsList[0]?.routeIdentifiers.vendor ?? ""}
    {@const stopCount = booking.detailsList.length - 1}

    {#if origDestLegs}
      {@const { originLeg, destinationLeg } = origDestLegs}
      <div class="booking">
        <em typography="label-medium">
          {originLeg.departureAt.toLocaleDateString($locale, {
            year: "numeric",
            month: "short",
            day: "numeric",
            timeZone: originLeg.origin.timeZone,
          })}
        </em>

        <div class="orig-dest">
          <span typography="title-medium" weight="bold">{originLeg.origin.name}</span>
          <em typography="title-small">{$t("words.to").toLowerCase()}</em>
          <span typography="title-medium" weight="bold">
            {destinationLeg.destination.name}
          </span>
        </div>

        <div class="vendor">
          <EntityAvatar name={vendor} />
          <span typography="label-medium">
            {vendor}
            {trainNumber} • {$t("words.stopCounter", { count: stopCount })}
          </span>
        </div>

        <div class="fare-info">
          <div class="time">
            <span typography="body-xsmall">{$t("words.departure")}</span>
            <strong typography="body-xlarge" weight="bold">
              {originLeg.departureAt.toLocaleTimeString($locale, {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: originLeg.origin.timeZone,
              })}
            </strong>
          </div>

          <div class="time">
            <span typography="body-xsmall">{$t("words.arrival")}</span>
            <strong typography="body-xlarge" weight="bold">
              {destinationLeg.arrivalAt.toLocaleTimeString($locale, {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: destinationLeg.destination.timeZone,
              })}
            </strong>
          </div>

          <div class="info-item">
            <span class="circle">
              <Icon variant="clock-filled" color="var(--color-main-primary-600)" />
            </span>

            <div>
              <em typography="body-xsmall">{$t("words.tripDuration")}</em>
              <strong typography="body-medium" weight="bold">
                {formatDuration(getTimeDeltaS(originLeg.departureAt, destinationLeg.arrivalAt))}
              </strong>
            </div>
          </div>

          <div class="info-item">
            <span class="circle">
              <Icon variant="seat" color="var(--color-main-primary-600)" />
            </span>

            <div>
              <em typography="body-xsmall">
                {$t("words.fareBrand", { count: cabinClasses.length })}
              </em>
              <strong typography="body-medium" weight="bold">
                {cabinClasses.join(", ")}
              </strong>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/each}
</div>

<style>
  .itinerary {
    display: flex;
    flex-flow: column;
    gap: 16px;
    color: var(--color-main-primary-900);
  }

  h3 {
    margin-bottom: 8px;
  }

  .booking {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .orig-dest > em {
    display: inline-block;
    padding: 0 8px;
  }

  .vendor {
    display: flex;
    gap: 8px;
    align-items: center;
    margin: 16px 0;
  }

  .fare-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px 24px;
  }

  .time {
    display: flex;
    flex-flow: column;
  }

  .time > span {
    color: var(--color-main-neutral-600);
  }

  .info-item {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .info-item > div {
    display: flex;
    flex-flow: column;
  }

  .info-item em {
    color: var(--color-main-primary-700);
  }

  .circle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-600) 1px solid;
    border-radius: 50%;
  }
</style>
