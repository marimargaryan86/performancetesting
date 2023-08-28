<script lang="ts" context="module">
  import type { OfferSegmentLegModel } from "models/booking/offer";

  function getOrigDestLegs(booking: BookingModel):
    | {
        originLeg: OfferSegmentLegModel;
        destinationLeg: OfferSegmentLegModel;
      }
    | undefined {
    const originLegs = booking.details[0]?.legs;
    const originLeg = originLegs?.[0];
    const destinationLegs = booking.details[booking.details.length - 1]?.legs;
    const destinationLeg = destinationLegs?.[destinationLegs.length - 1];

    if (originLeg && destinationLeg) {
      return { originLeg, destinationLeg };
    }

    return undefined;
  }
</script>

<script lang="ts">
  import ClockIcon from "components/icons/clock-icon.svelte";
  import type { BookingModel } from "models/booking/order";
  import { formatDuration } from "formatting/date-time";
  import { getTimeDeltaS } from "utils/date-time";
  import SeatIcon from "components/icons/seat-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";

  export let bookings: BookingModel[];
</script>

<div class="itinerary">
  <h3 class="typography body-large bold">Itinerary details</h3>

  {#each bookings as booking}
    {@const origDestLegs = getOrigDestLegs(booking)}
    {@const cabinClasses = booking.details.map((item) => item.cabinClassName)}
    {@const operator = booking.details[0]?.operator ?? "Unknown"}
    {@const segmentCount = booking.details.length}

    {#if origDestLegs}
      {@const { originLeg, destinationLeg } = origDestLegs}
      <div class="booking">
        <em class="typography label-medium">
          {originLeg.departureAt.toLocaleDateString("en-GB", {
            year: "numeric",
            month: "short",
            day: "numeric",
            timeZone: originLeg.origin.timeZone,
          })}
        </em>

        <div class="orig-dest">
          <span class="typography title-medium bold">{originLeg.origin.name}</span>
          <em class="typography title-small">to</em>
          <span class="typography title-medium bold">
            {destinationLeg.destination.name}
          </span>
        </div>

        <div class="operator">
          <EntityAvatar name={operator} />
          <span class="typography label-medium">
            {operator}
            •
            {segmentCount === 1 ? "Direct" : `${segmentCount} stops`}
          </span>
        </div>

        <div class="fare-info">
          <div class="time">
            <span class="typography body-xsmall">Departure</span>
            <strong class="typography body-xlarge bold">
              {originLeg.departureAt.toLocaleTimeString("sv-SE", {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: originLeg.origin.timeZone,
              })}
            </strong>
          </div>

          <div class="time">
            <span class="typography body-xsmall">Arrival</span>
            <strong class="typography body-xlarge bold">
              {destinationLeg.arrivalAt.toLocaleTimeString("sv-SE", {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: destinationLeg.destination.timeZone,
              })}
            </strong>
          </div>

          <div class="info-item">
            <span class="circle">
              <ClockIcon color="var(--color-main-primary-600)" />
            </span>

            <div>
              <em class="typography body-xsmall">Trip duration</em>
              <strong class="typography body-medium bold">
                {formatDuration(getTimeDeltaS(originLeg.departureAt, destinationLeg.arrivalAt))}
              </strong>
            </div>
          </div>

          <div class="info-item">
            <span class="circle">
              <SeatIcon color="var(--color-main-primary-600)" />
            </span>

            <div>
              <em class="typography body-xsmall">
                Fare class{cabinClasses.length === 1 ? "" : "es"}
              </em>
              <strong class="typography body-medium bold">
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

  .operator {
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
