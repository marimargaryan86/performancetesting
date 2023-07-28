<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { onMount } from "svelte";
  import { page } from "$app/stores";

  export let offer;
  export let fare;

  let passengerInfo = "";
  let expanded = false;

  function toggleExpanded(): void {
    expanded = !expanded;
  }

  onMount(() => {
    const urlParams = $page.url.searchParams;
    const adults = Number(urlParams.get("adults"));
    const children = Number(urlParams.get("children"));
    const infants = Number(urlParams.get("infants"));
    passengerInfo = `${adults} Adult${adults > 1 ? "s" : ""}${children > 0 ? "," : ""}
    ${children > 0 ? `${children} Child${children > 1 ? "ren" : ""}` : ""}${infants > 0 ? "," : ""}
    ${infants > 0 ? `${infants} Infant${infants > 1 ? "s" : ""}` : ""}`;
  });
</script>

<div class="summary">
  <h3>Summary</h3>
  <p class="typography body-xlarge-weight-600">
    {offer?.departureStation} <span class="typography body-medium">to</span>
    {offer?.arrivalStation}
  </p>
  <div>
    <div class="typography body-medium">Passengers</div>
    <div class="typography body-medium-weight-600">{passengerInfo}</div>
  </div>
  <hr />
  <div class="itinerary-details typography body-medium-weight-600" on:click={toggleExpanded}>
    Itinerary details
    <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-main-primary-500)" />
  </div>
  {#if expanded}
    <div class="typography body-medium">Outbound</div>
    <div class="offer-info typography body-medium-weight-600">
      <div class="offer-direction">
        <div class="circle" />
        <div class="line" />
        <div class="circle" />
      </div>
      <div class="offer-time">
        <div class="departure-time">{offer?.departureTime}</div>
        <div class="journey-duration grey-color typography body-small">
          {offer?.journeyDuration}
        </div>
        <div class="arrival-time">{offer?.arrivalTime}</div>
      </div>
      <div class="offer-stations">
        <div class="departure-station station">
          <span>{offer?.departureStation}</span>
          <span class="grey-color station-info typography body-small"
            >{offer?.departureStationInfo}</span
          >
        </div>
        <div class="arrival-station station">
          <span>{offer?.arrivalStation}</span>
          <span class="grey-color station-info typography body-small"
            >{offer?.arrivalStationInfo}</span
          >
        </div>
      </div>
    </div>
  {/if}
  <hr />
  <p class="typography body-small">The price is for all passengers</p>
  <div class="prices typography body-small">
    <div>
      <p>Base far</p>
      <p class="typography body-small-weight-600">€80.00</p>
    </div>
    <div>
      <p>Taxes</p>
      <p class="typography body-small-weight-600">€10.00</p>
    </div>
    <div>
      <p>Agency mark-up</p>
      <p class="typography body-small-weight-600">€2.50</p>
    </div>
    <div>
      <p>Contractual mark-up</p>
      <p class="typography body-small-weight-600">€2.50</p>
    </div>
  </div>
  <div class="total-price typography body-xlarge-weight-600">
    <p>Total to pay</p>
    <p>€{fare?.price}</p>
  </div>
  <div class="caution">
    <p class="typography body-x-small">
      Fares are not guaranteed until full payment is received and tickets are issued. See all the
      applicable
      <a href="#" class="caution-link">Fare Rules</a> and
      <a href="#" class="caution-link">Baggage Information.</a>
    </p>
  </div>
</div>

<style>
  .summary {
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-content: flex-end;
    min-width: 320px;
    max-width: 320px;
    padding: 40px 24px 32px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  h3 {
    margin-bottom: 8px;
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  hr {
    width: 100%;
    border: none;
    border-top: 1px solid var(--color-common-line-medium);
  }

  .itinerary-details {
    display: flex;
    align-items: center;
    align-self: stretch;
    justify-content: space-between;
    color: var(--color-main-primary-500);
    cursor: pointer;
  }

  .offer-info {
    display: flex;
    margin-bottom: 10px;
  }

  .offer-direction {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
    width: 16px;
  }

  .offer-time {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-left: 12px;
  }

  .circle {
    width: 16px;
    height: 16px;
    border: 1px solid #000000;
    border-radius: 50%;
  }

  .line {
    height: 24px;
    border-left: 1px solid var(--color-main-neutral-500);
  }

  .offer-stations {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-left: 17px;
  }

  .station {
    position: relative;
    display: flex;
    flex-direction: column;
  }

  .station-info {
    position: absolute;
    top: 24px;
  }

  .grey-color {
    color: var(--color-main-neutral-500);
  }

  .prices {
    display: flex;
    flex-direction: column;
  }

  .prices div {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .total-price {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .total-price :last-child {
    color: var(--color-main-primary-500);
  }

  .caution-link {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
