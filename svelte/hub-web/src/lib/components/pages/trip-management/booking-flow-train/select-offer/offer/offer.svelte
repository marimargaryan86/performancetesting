<script lang="ts">
  import EntityAvatar from "$lib/components/ui/entity-avatar.svelte";
  import { formatAmount } from "$lib/formatting/currency";
  import { formatDuration, formatTime } from "$lib/formatting/date-time";
  import AlternativeFares from "./alternative-fares.svelte";
  import { createEventDispatcher, type ComponentEvents } from "svelte";
  import { getTimeDeltaS } from "$lib/utils/date-time";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { ensureDefined } from "$lib/utils/array";
  import { getLocale, getTranslator } from "$lib/i18n";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { getCheapestOption, getTotalPrice } from "$lib/utils/offer";

  export let offer: MobileSchemas.Offer;
  export let selectedOptionIds: string[] | undefined;
  export let selected: boolean;
  export let pending: boolean;

  const locale = getLocale();
  const t = getTranslator();
  const dispatch = createEventDispatcher<{
    select: { proceed: boolean; offerId: string; optionIds: string[] };
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
    dispatch("select", {
      proceed: true,
      offerId: offer.id,
      optionIds: selectedOption.map((item) => item.id),
    });
  }

  function selectOption(event: ComponentEvents<AlternativeFares>["select"]): void {
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

    dispatch("select", {
      proceed: false,
      offerId: offer.id,
      optionIds: nextSelectedOptions.map((item) => item.id),
    });
  }
</script>

<div class="offer" class:selected>
  {#each offer.groups as group, groupIdx}
    {@const vendor = group.detailsList[0]?.vendor ?? $t("words.unknown")}
    {@const trainNumber = group.detailsList[0]?.routeIdentifiers.vendor ?? ""}
    {@const stopCount = (group.detailsList?.length ?? 1) - 1}

    <div class="group">
      <div class="header" typography="label-medium">
        <EntityAvatar name={vendor} size="24px" />
        <span>
          {vendor}
          {trainNumber} • {$t("words.stopCounter", { count: stopCount })}
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
                      {formatTime(leg.departureAt, $locale, { timeZone: leg.origin.timeZone })}
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
                      {formatTime(leg.arrivalAt, $locale, { timeZone: leg.destination.timeZone })}
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
              <em typography="label-medium">{$t("sentences.startingAt")}</em>
              <strong typography="title-large" weight="bold">
                {formatAmount(totalPrice, $locale, { sign: true })}
              </strong>
            </span>

            <button size="x-small" variant="outline" on:click={selectOffer}>
              {$t("actions.bookNow")}

              {#if selected && pending}
                <LoadingIcon color="var(--color-main-primary-500)" />
              {/if}
            </button>
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
