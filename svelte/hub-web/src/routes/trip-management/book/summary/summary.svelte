<script lang="ts" context="module">
  function getPassengersPresentation(passengers: PassengerCountData): string {
    const { adults, children, infants } = passengers;

    return [
      adults ? `${adults} Adult${adults === 1 ? "" : "s"}` : undefined,
      children ? `${children} Child${children === 1 ? "" : "ren"}` : undefined,
      infants ? `${infants} Infant${infants === 1 ? "" : "s"}` : undefined,
    ]
      .filter(ensureDefined)
      .join(", ");
  }

  export type OrigDestLegs = {
    originLeg: Infer<typeof offerSegmentLegModel>;
    destinationLeg: Infer<typeof offerSegmentLegModel>;
  };

  function getOrigDestLegs(group: Infer<typeof offerGroupModel>): OrigDestLegs | undefined {
    const segments = [...group.details].sort((a, b) => a.sequences.segment - b.sequences.segment);
    const startSegment = segments[0];
    const endSegment = segments[segments.length - 1];

    if (!(startSegment && endSegment)) {
      return undefined;
    }

    const originLeg = startSegment.legs[0];
    const destinationLeg = endSegment.legs[endSegment.legs.length - 1];

    if (!(originLeg && destinationLeg)) {
      return undefined;
    }

    return { originLeg, destinationLeg };
  }

  function getPriceBreakdown(
    options: Infer<typeof offerOptionModel>[],
  ): Infer<typeof priceBreakdownModel>[] {
    const priceBreakdown: Infer<typeof priceBreakdownModel>[] = [];

    options.forEach((option) => {
      option.priceBreakdown?.forEach((item) => {
        const existing = priceBreakdown.find((pb) => pb.type === item.type);

        if (existing) {
          existing.price = { ...existing.price, amount: existing.price.amount + item.price.amount };
        } else {
          priceBreakdown.push({ ...item });
        }
      });
    });

    return priceBreakdown;
  }

  function getTotalPrice(options: Infer<typeof offerOptionModel>[]): Infer<typeof priceModel> {
    return options.reduce<Infer<typeof priceModel>>(
      (prev, curr) => ({
        amount: prev.amount + curr.price.amount,
        currency: curr.price.currency,
      }),
      { amount: 0, currency: "EUR" },
    );
  }
</script>

<script lang="ts">
  import type { PassengerCountData } from "../common";
  import { formatAmount, formatPriceBreakdownType } from "formatting/currency";
  import Itinerary from "./itinerary.svelte";
  import type {
    offerGroupModel,
    offerModel,
    offerOptionModel,
    offerSegmentLegModel,
  } from "integration/junction-mobile-api/schemas/offer";
  import type { Infer } from "integration/junction-mobile-api/schema-model.server";
  import type {
    priceBreakdownModel,
    priceModel,
  } from "integration/junction-mobile-api/schemas/price";
  import { ensureDefined } from "utils/array";

  export let passengers: PassengerCountData;
  export let options: Infer<typeof offerOptionModel>[] = [];
  export let offer: Infer<typeof offerModel> | undefined = undefined;

  $: offerGroups = offer?.groups ?? [];
  $: origDestLegsList = offerGroups.map((item) => getOrigDestLegs(item)).filter(ensureDefined);
  $: priceBreakdown = getPriceBreakdown(options);
  $: totalPrice = getTotalPrice(options);
  $: fareBrands = options.map((item) => item.brandName);
</script>

<div class="summary">
  <h2 class="typography title-large bold">Summary</h2>

  {#each origDestLegsList as { originLeg, destinationLeg }}
    <h3 class="orig-dest">
      <strong class="typography title-medium bold">
        {originLeg.origin.name}
        <span class="typography title-small default">to</span>
      </strong>
      <strong class="typography title-medium bold">
        {destinationLeg.destination.name}
      </strong>
    </h3>
  {/each}

  <div class="passengers">
    <strong class="typography label-large">Passengers</strong>
    <span class="typography label-large bold">{getPassengersPresentation(passengers)}</span>
  </div>

  <div class="fare-brand">
    <strong class="typography label-large">Fare Brand{fareBrands.length === 1 ? "" : "s"}</strong>
    <span class="typography label-large bold">{fareBrands.join(", ")}</span>
    <button class="typography body-small">View fare rules</button>
  </div>

  <hr />

  <Itinerary {origDestLegsList} />

  <hr />

  <div class="price typography body-small">
    <span>The price is for all passengers</span>
    <ul>
      {#each priceBreakdown as item}
        <li>
          <span>{formatPriceBreakdownType(item.type)}</span>
          <strong class="typography bold">{formatAmount(item.price, undefined, true)}</strong>
        </li>
      {/each}
    </ul>

    <strong class="total typography body-xlarge bold">
      <span>Total to pay</span>
      <em>{formatAmount(totalPrice, undefined, true)}</em>
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
