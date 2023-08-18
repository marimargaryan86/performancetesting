<script lang="ts" context="module">
  function getPassengersPresentation(passengers: PassengerData[]): string {
    const adults = passengers.filter((item) => item.type === "adult").length;
    const children = passengers.filter((item) => item.type === "child").length;
    const infants = passengers.filter((item) => item.type === "infant").length;

    return [
      adults ? `${adults} Adult${adults === 1 ? "" : "s"}` : undefined,
      children ? `${children} Child${children === 1 ? "" : "ren"}` : undefined,
      infants ? `${infants} Infant${infants === 1 ? "" : "s"}` : undefined,
    ]
      .filter((item): item is string => Boolean(item))
      .join(", ");
  }
</script>

<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { PassengerData } from "./passengers.svelte";

  export let passengers: PassengerData[];
</script>

<div class="summary">
  <h2 class="typography title-large bold">Summary</h2>
  <h3 class="orig-dest">
    <strong class="typography title-medium bold">
      Malaga Maria Zambrano
      <span class="typography title-small default">to</span>
    </strong>
    <strong class="typography title-medium bold">Barcelona Sants</strong>
  </h3>

  <div class="passengers">
    <strong class="typography label-large">Passengers</strong>
    <span class="typography label-large bold">{getPassengersPresentation(passengers)}</span>
  </div>

  <div class="fare-brand">
    <strong class="typography label-large">Fare Brand</strong>
    <span class="typography label-large bold">Standard flex</span>
    <button class="typography body-small">View fare rules</button>
  </div>

  <hr />

  <div class="itinerary">
    <button class="typography title-small bold">
      Itinerary Details
      <ChevronIcon direction="down" />
    </button>
  </div>

  <hr />

  <div class="price typography body-small">
    <span>The price is for all passengers</span>
    <ul>
      <li>
        <span>Base fare</span>
        <strong class="typography bold">€80.00</strong>
      </li>
      <li>
        <span>Taxes</span>
        <strong class="typography bold">€80.00</strong>
      </li>
      <li>
        <span>Fees</span>
        <strong class="typography bold">€80.00</strong>
      </li>
      <li>
        <span>Agency mark-up</span>
        <strong class="typography bold">€80.00</strong>
      </li>
      <li>
        <span>Contractual mark-up</span>
        <strong class="typography bold">€80.00</strong>
      </li>
    </ul>

    <strong class="total typography body-xlarge bold">
      <span>Total to pay</span>
      <em>€149.00</em>
    </strong>
  </div>

  <div class="disclaimer typography body-xsmall">
    Fares are not guaranteed until full payment is received and tickets are issued. See all the
    applicable
    <button class="typography body-xsmall">Fare Rules</button>
    and
    <button class="typography body-xsmall">Baggage Information</button>.
  </div>
</div>

<style>
  .summary {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 24px;
    overflow-y: auto;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .orig-dest,
  .passengers,
  .fare-brand,
  .itinerary,
  .price,
  .price > ul {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .price {
    gap: 16px;
  }

  .orig-dest,
  .price > ul {
    gap: 4px;
  }

  .price > ul > li,
  .total {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .fare-brand > button {
    align-self: flex-end;
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: underline;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  hr {
    margin: 0;
    border: 0;
    border-top: var(--color-common-line-medium) 1px solid;
  }

  .itinerary {
    gap: 0;
  }

  .itinerary > button {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .itinerary > button > :global(svg) {
    flex-shrink: 0;
  }

  .total > em {
    color: var(--color-main-primary-500);
  }

  .disclaimer > button {
    padding: 0;
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
