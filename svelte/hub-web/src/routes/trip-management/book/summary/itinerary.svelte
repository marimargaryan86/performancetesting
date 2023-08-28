<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { OrigDestLegs } from "./summary.svelte";
  import { formatDuration } from "formatting/date-time";
  import { getTimeDeltaS } from "utils/date-time";
  import { slideFade } from "transitions/slide-fade";

  let expanded = false;

  function expand(): void {
    expanded = true;
  }

  function collapse(): void {
    expanded = false;
  }

  function toggle(): void {
    if (expanded) {
      collapse();
    } else {
      expand();
    }
  }

  export let origDestLegsList: OrigDestLegs[];
</script>

<div class="itinerary">
  <button class="typography title-small bold" on:click={toggle}>
    Itinerary Details
    <ChevronIcon direction={expanded ? "up" : "down"} />
  </button>

  {#if expanded}
    <ul class="segments" transition:slideFade={{ duration: 300 }}>
      {#each origDestLegsList as { originLeg, destinationLeg }}
        <li class="segment typography label-large bold">
          <span class="circle" />
          <strong>
            {originLeg.departureAt.toLocaleTimeString("sv-SE", {
              hour: "2-digit",
              minute: "2-digit",
              timeZone: originLeg.origin.timeZone,
            })}
          </strong>
          <strong>{originLeg.origin.name}</strong>

          <span class="line" />
          <em class="typography body-small default">
            {formatDuration(getTimeDeltaS(originLeg.departureAt, destinationLeg.arrivalAt))}
          </em>
          <em />

          <span class="circle" />
          <strong>
            {destinationLeg.arrivalAt.toLocaleTimeString("sv-SE", {
              hour: "2-digit",
              minute: "2-digit",
              timeZone: destinationLeg.destination.timeZone,
            })}
          </strong>
          <strong>{destinationLeg.destination.name}</strong>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .itinerary {
    display: flex;
    flex-flow: column;
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

  .segments {
    display: flex;
    flex-flow: column;
    gap: 16px;
    margin-top: 16px;
  }

  .segment {
    display: grid;
    grid-template-columns: 16px max-content 1fr;
    gap: 8px 12px;
    align-items: center;
  }

  .circle {
    display: block;
    width: 16px;
    height: 16px;
    border: var(--color-common-light-strong) 1px solid;
    border-radius: 50%;
  }

  .line {
    justify-self: center;
    width: 0;
    height: 24px;
    border-right: var(--color-main-neutral-500) 1px solid;
  }

  em {
    color: var(--color-main-neutral-500);
  }
</style>
