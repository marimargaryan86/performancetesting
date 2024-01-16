<script lang="ts" context="module">
  function formatTime(time: Date, timeZone: string, locale: Locale): string {
    return time.toLocaleTimeString(locale, {
      timeZone,
      minute: "2-digit",
      hour: "2-digit",
    });
  }

  function getTotalPrice(options: OfferOption[]): Price {
    return options.reduce<Price>(
      (prev, curr) => (prev.amount < curr.price.total.amount ? prev : curr.price.total),
      options[0]?.price.total ?? { amount: 0, currency: "EUR" },
    );
  }

  function getCheapestOption(options: OfferOption[]): OfferOption {
    const initialOption = options[0];

    if (!initialOption) {
      throw new Error("No options available");
    }

    return options.reduce((prev, curr) => {
      return prev.price.total.amount <= curr.price.total.amount ? prev : curr;
    }, initialOption);
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
  import type { Offer, OfferOption } from "integration/junction-mobile-api/schemas/offer";
  import type { Price } from "integration/common/schemas/price";
  import { ensureDefined } from "utils/array";
  import { getLocale, getLocaleData, type Locale } from "i18n";
  import { formatStopCount } from "formatting/trip";

  export let offer: Offer;
  export let selectedOptionIds: string[] | undefined;
  export let selected: boolean;

  const locale = getLocale();
  const i18n = getLocaleData();
  const dispatch = createEventDispatcher<{
    select: { offerId: string; optionIds: string[] };
    markSelection: { offerId: string; optionIds: string[] };
  }>();

  $: selectedOption = offer.groups
    .map((group) => {
      const optionIds = selectedOptionIds;

      if (optionIds) {
        return group.options.find((item) => optionIds.includes(item.id));
      }

      return getCheapestOption(group.options);
    })
    .filter(ensureDefined);

  $: totalPrice = getTotalPrice(selectedOption);

  function selectOffer(): void {
    dispatch("select", { offerId: offer.id, optionIds: selectedOption.map((item) => item.id) });
  }

  function selectOption(event: CustomEvent<OfferOption>): void {
    const nextSelectedOptions = offer.groups
      .map((group) => {
        if (group.options.find((option) => option.id === event.detail.id)) {
          return event.detail;
        }

        return selectedOption.find((option) =>
          group.options.find((option2) => option.id === option2.id),
        );
      })
      .filter(ensureDefined);

    dispatch("markSelection", {
      offerId: offer.id,
      optionIds: nextSelectedOptions.map((item) => item.id),
    });
  }
</script>

<div class="offer" class:selected>
  {#each offer.groups as group, groupIdx}
    {@const vendor = group.detailsList[0]?.vendor ?? $i18n.words.unknown}
    {@const trainNumber = group.detailsList[0]?.routeIdentifiers.vendor ?? ""}
    {@const stopCount = group.detailsList?.length ?? 1}

    <div class="group">
      <div class="header" typography="label-medium">
        <EntityAvatar name={vendor} size="24px" />
        <span>
          {vendor}
          {trainNumber} • {formatStopCount(stopCount, $i18n)}
        </span>
      </div>

      <div class="info">
        <div class="segments">
          {#each group.detailsList as details}
            <span typography="body-small">
              {details.legs[0]?.departureAt.toLocaleDateString($locale, {
                month: "long",
                day: "numeric",
                year: "numeric",
                timeZone: details.legs[0]?.origin.timeZone,
              })}
            </span>

            <ul class="legs">
              {#each details.legs ?? [] as leg}
                <li class="leg">
                  <div class="route">
                    <span class="circle" />
                    <span class="time" typography="label-large" weight="bold">
                      {formatTime(leg.departureAt, leg.origin.timeZone, $locale)}
                    </span>
                    <span class="location" typography="label-large" weight="bold">
                      {leg.origin.name}
                    </span>

                    <span class="line" />
                    <span class="duration" typography="body-small">
                      {formatDuration(getTimeDeltaS(leg.arrivalAt, leg.departureAt))}
                    </span>
                    <span />

                    <span class="circle" />
                    <span class="time" typography="label-large" weight="bold">
                      {formatTime(leg.arrivalAt, leg.destination.timeZone, $locale)}
                    </span>
                    <span class="location" typography="label-large" weight="bold">
                      {leg.destination.name}
                    </span>
                  </div>
                </li>
              {/each}
            </ul>
          {/each}
        </div>

        {#if groupIdx === 0}
          <div class="price">
            <span>
              <em typography="label-medium">{$i18n.sentences.startingAt}</em>
              <strong typography="title-large" weight="bold">
                {formatAmount(totalPrice, { locale: $locale, sign: true })}
              </strong>
            </span>

            <Button size="x-small" variant="outline" on:click={selectOffer}>
              {$i18n.actions.bookNow}
            </Button>
          </div>
        {/if}
      </div>

      <AlternativeFares
        options={group.options}
        selectedOptions={selectedOption}
        on:select={selectOption}
      />
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
