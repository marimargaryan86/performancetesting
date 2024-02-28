<script lang="ts">
  import Icon from "$lib/components/icons/icon.svelte";
  import { formatDuration } from "$lib/formatting/date-time";

  import { getLocale, getTranslator } from "$lib/i18n";
  import { ensureDefined } from "$lib/utils/array";
  import { getLegExtremes } from "$lib/utils/offer";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

  const t = getTranslator();
  const locale = getLocale();

  export let detailsList: MobileSchemas.TripOfferGroupDetails[];

  $: ({ start: tripStartLeg } = getLegExtremes(detailsList[0]));
</script>

<div class="itinerary">
  <span typography="body-large" weight="bold" class="date">
    {tripStartLeg?.departureAt.toLocaleDateString($locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: tripStartLeg.origin.timeZone,
    })}

    <span typography="body-small" weight="default">
      {$t("words.stopCounter", { count: detailsList.length - 1 })}
    </span>
  </span>

  <ul class="segments">
    {#each detailsList as details}
      {@const operator = [
        details.vendor.length ? details.vendor : details.routeIdentifiers.operator,
        details.operator?.length ? details.operator : details.routeIdentifiers.vendor,
      ]
        .filter(ensureDefined)
        .join(" ")}
      {@const { start: startLeg, end: endLeg } = getLegExtremes(details)}

      <li typography="body-xsmall" class="operator">
        <Icon variant="train" size="13px" color="var(--color-main-primary-700)" />
        {operator}
      </li>

      <li class="segment">
        <ul class="legs" typography="label-large">
          {#each [startLeg, endLeg] as leg, idx}
            {@const durationMs = endLeg.arrivalAt.getTime() - startLeg.departureAt.getTime()}
            {@const time = idx === 0 ? leg.departureAt : leg.arrivalAt}
            {@const place = idx === 0 ? leg.origin : leg.destination}

            <li class="leg">
              <span class="waypoint" />
              <span weight="bold">
                {time.toLocaleTimeString($locale, {
                  hour: "2-digit",
                  minute: "2-digit",
                  timeZone: place.timeZone,
                })}
              </span>
              <span>{place.name}</span>

              {#if idx === 0}
                <span class="route" />
                <span typography="body-small" class="duration">
                  {formatDuration(durationMs / 1000)}
                </span>
              {/if}
            </li>
          {/each}
        </ul>
      </li>
    {/each}
  </ul>
</div>

<style>
  .itinerary {
    display: flex;
    flex-flow: column;
    gap: 4px;
  }

  .date {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .date > span {
    color: var(--color-main-primary-700);
  }

  .segments {
    display: grid;
    grid-template-columns: max-content max-content 1fr;
    gap: 4px 16px;
  }

  .segment {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
  }

  .operator {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
    align-items: center;
    color: var(--color-main-primary-700);
  }

  .legs {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
  }

  .leg {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
    align-items: center;
  }

  .waypoint {
    width: 13px;
    height: 13px;
    border: var(--color-main-neutral-600) 1px solid;
    border-radius: 50%;
  }

  .route {
    justify-self: center;
    width: 1px;
    height: 24px;
    background-color: var(--color-main-neutral-500);
  }

  .duration {
    color: var(--color-main-neutral-500);
  }
</style>
