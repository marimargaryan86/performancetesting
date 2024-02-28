<script lang="ts">
  import { getLocale } from "$lib/i18n";
  import type { DirectionX } from "$lib/models/spatial";
  import Route from "./route.svelte";
  import type * as CommonSchemas from "~/integration/common/schemas";

  const locale = getLocale();

  let className: string | undefined = undefined;
  export { className as class };
  export let start: CommonSchemas.OfferSegmentLeg | undefined;
  export let end: CommonSchemas.OfferSegmentLeg | undefined;
  export let title: string;
  export let direction: DirectionX;
  export let focused: boolean;
  export let showTripDirection = true;
</script>

<div class:trip-summary={true} class={className} class:focused>
  <div class="info">
    {#if showTripDirection}
      <span typography="body-medium" weight="bold">
        <span class="arrow" typography="body-large" weight="bold">
          {#if direction === "left"}
            {"<-"}
          {:else}
            {"->"}
          {/if}
        </span>

        {title}
      </span>
    {/if}

    {#if start}
      <span typography="body-small" class="date">
        {start.departureAt.toLocaleDateString($locale, {
          year: "numeric",
          month: "long",
          day: "numeric",
          timeZone: start.origin.timeZone,
        })}
      </span>

      {#if showTripDirection}
        <slot name="action" />
      {/if}
    {/if}
  </div>

  {#if start && end}
    <Route
      legs={[
        {
          origin: start.origin,
          destination: end.destination,
          departureAt: start.departureAt,
          arrivalAt: end.arrivalAt,
        },
      ]}
    />
  {/if}
</div>

<style>
  .trip-summary {
    display: flex;
    gap: 8px;
    align-self: stretch;
    min-height: 84px;
    padding: 8px;
    border: transparent 2px solid;
    border-radius: 8px;
    transition: border-color 300ms ease;
  }

  .trip-summary.focused {
    border-color: var(--color-main-primary-400);
  }

  .info {
    display: flex;
    flex-flow: column;
    align-items: flex-end;
  }

  .arrow {
    color: var(--color-main-primary-500);
  }

  .date {
    display: flex;
    flex-grow: 1;
    align-items: center;
  }
</style>
