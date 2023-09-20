<script lang="ts" context="module">
  function formatTime(time: Date, timeZone: string): string {
    return time.toLocaleTimeString("en-GB", {
      timeZone,
      minute: "2-digit",
      hour: "2-digit",
    });
  }

  function getTotalPrice(options: OfferOptionModel[]): PriceModel {
    return options.reduce<PriceModel>(
      (prev, curr) => (prev.amount < curr.price.amount ? prev : curr.price),
      options[0]?.price ?? { amount: 0, currency: "EUR" },
    );
  }
</script>

<script lang="ts">
  import Button from "components/ui/button.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import { formatAmount } from "formatting/currency";
  import { formatDuration } from "formatting/date-time";
  import AlternativeFares from "./alternative-fares.svelte";
  import { createEventDispatcher } from "svelte";
  import { getTimeDeltaS } from "utils/date-time";
  import type { OfferModel, OfferOptionModel } from "integration/junction-mobile-api/schemas/offer";
  import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
  import { ensureDefined } from "utils/array";

  export let offer: OfferModel;
  export let selectedOptionIds: string[] | undefined;
  export let selected: boolean;

  const dispatch = createEventDispatcher<{
    select: { offerId: string; optionIds: string[] };
  }>();

  $: selectedOptions = offer.groups
    .map((group) => {
      const optionIds = selectedOptionIds;

      if (optionIds) {
        return group.options.find((item) => optionIds.includes(item.id));
      }

      return group.options[0];
    })
    .filter(ensureDefined);

  $: totalPrice = getTotalPrice(selectedOptions);

  function selectOffer(): void {
    dispatch("select", { offerId: offer.id, optionIds: selectedOptions.map((item) => item.id) });
  }

  function selectOption(event: CustomEvent<OfferOptionModel>): void {
    const nextSelectedOptions = offer.groups
      .map((group) => {
        if (group.options.find((option) => option.id === event.detail.id)) {
          return event.detail;
        }

        return selectedOptions.find((option) =>
          group.options.find((option2) => option.id === option2.id),
        );
      })
      .filter(ensureDefined);

    dispatch("select", {
      offerId: offer.id,
      optionIds: nextSelectedOptions.map((item) => item.id),
    });
  }
</script>

<div class="offer" class:selected>
  {#each offer.groups as group, groupIdx}
    {@const vendor = group.details[0]?.vendor ?? "Unknown"}
    {@const stopCount = group.details[0]?.legs.length ?? 1}

    <div class="group">
      <div class="header typography label-medium">
        <EntityAvatar name={vendor} size="24px" />
        <span>
          {vendor}
          •
          {stopCount === 1 ? "Direct" : `${stopCount} stops`}
        </span>
      </div>

      <div class="info">
        <div class="segments">
          {#each group.details as details}
            <span class="typography body-small">
              {details.legs[0]?.departureAt.toLocaleDateString("en-GB", {
                month: "long",
                day: "numeric",
                year: "numeric",
              })}
            </span>

            <ul class="legs">
              {#each details.legs ?? [] as leg}
                <li class="leg">
                  <div class="route">
                    <span class="circle" />
                    <span class="time typography label-large bold">
                      {formatTime(leg.departureAt, leg.origin.timeZone)}
                    </span>
                    <span class="location typography label-large bold">{leg.origin.name}</span>

                    <span class="line" />
                    <span class="duration typography body-small">
                      {formatDuration(getTimeDeltaS(leg.arrivalAt, leg.departureAt))}
                    </span>
                    <span />

                    <span class="circle" />
                    <span class="time typography label-large bold">
                      {formatTime(leg.arrivalAt, leg.destination.timeZone)}
                    </span>
                    <span class="location typography label-large bold">{leg.destination.name}</span>
                  </div>
                </li>
              {/each}
            </ul>
          {/each}
        </div>

        {#if groupIdx === 0}
          <div class="price">
            <span>
              <em class="typography label-medium">From</em>
              <strong class="typography title-large bold">
                {formatAmount(totalPrice, undefined, true)}
              </strong>
            </span>

            <Button size="x-small" variant="outline" on:click={selectOffer}>Book now</Button>
          </div>
        {/if}
      </div>

      <AlternativeFares options={group.options} {selectedOptions} on:select={selectOption} />
    </div>
  {/each}
</div>

<style>
  .offer {
    display: flex;
    flex-flow: column;
    gap: 8px;
    padding: 8px 22px 22px;
    background-color: var(--color-common-background-light-main);
    border: transparent 2px solid;
    border-top-width: 16px;
    border-radius: 16px;
    transition: border-color 200ms ease;
  }

  .offer.selected {
    border-color: var(--color-main-primary-600);
  }

  .group {
    display: flex;
    flex-flow: column;
    gap: 12px;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .info {
    display: flex;
    gap: 24px;
  }

  .segments {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 8px;
  }

  .route {
    display: grid;
    grid-template-columns: repeat(3, max-content);
    gap: 12px;
    padding: 8px 0;
  }

  .circle {
    display: block;
    width: 16px;
    height: 16px;
    border: var(--color-common-light-strong) 1px solid;
    border-radius: 50%;
  }

  .line {
    display: block;
    justify-self: center;
    width: 1px;
    height: 100%;
    min-height: 40px;
    border-left: var(--color-main-neutral-500) 1px solid;
  }

  .duration {
    align-self: center;
    color: var(--color-main-neutral-500);
  }

  .price {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-items: flex-end;
    justify-content: center;
    padding-left: 24px;
    border-left: var(--color-main-neutral-200) 1px solid;
  }

  .price > span {
    display: flex;
    gap: 4px;
    align-items: center;
  }
</style>
