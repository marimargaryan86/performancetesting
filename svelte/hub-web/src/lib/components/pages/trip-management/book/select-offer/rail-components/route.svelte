<script lang="ts">
  import { formatDuration } from "$lib/formatting/date-time";
  import { getLocale } from "$lib/i18n";
  import type * as CommonSchemas from "~/integration/common/schemas";

  const locale = getLocale();

  export let legs: CommonSchemas.OfferSegmentLeg[];
</script>

<ul class="legs" typography="label-large">
  {#each legs as leg, idx}
    {@const durationMs = leg.arrivalAt.getTime() - leg.departureAt.getTime()}

    <li class="leg">
      <span class="waypoint" />
      <span weight="bold">
        {leg.departureAt.toLocaleTimeString($locale, {
          hour: "2-digit",
          minute: "2-digit",
          timeZone: leg.origin.timeZone,
        })}
      </span>
      <span>{leg.origin.name}</span>

      <span class="route" />
      <span typography="body-small" class="duration">
        {formatDuration(durationMs / 1000)}
      </span>
    </li>

    {#if idx === legs.length - 1}
      <li class="leg">
        <span class="waypoint" />
        <span weight="bold">
          {leg.arrivalAt.toLocaleTimeString($locale, {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: leg.destination.timeZone,
          })}
        </span>
        <span>{leg.destination.name}</span>
      </li>
    {/if}
  {/each}
</ul>

<style>
  .legs {
    display: grid;
    grid-template-columns: max-content max-content 1fr;
    gap: 0 16px;
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
