<script lang="ts">
  import { origins } from "$lib/data/constants";
  import Accordion from "$lib/components/accordion.svelte";
  import type { Place } from "$lib/models/common";

  export let dropdown = "";

  export let selectedOrigin: string = "";

  let originCategories: Record<string, Place[]> = origins.reduce(
    (acc, origin) => ({
      ...acc,
      [origin.country]: [...(acc[origin.country as keyof typeof acc] || []), origin],
    }),
    {},
  );

  $: selectedOrigin !== "" && (dropdown = "");
</script>

<div class="dropdown">
  {#each Object.entries(originCategories) as [country, category]}
    <Accordion>
      <span slot="head">All {country} airports</span>
      <div slot="details">
        <ul>
          {#each category as airport}
            <label for={airport.id}>
              <input
                id={airport.id}
                type="radio"
                class="airport-option"
                value={airport.id}
                bind:group={selectedOrigin}
                hidden
              />
              <p class="airport-label">{airport.name}</p>
            </label>
          {/each}
        </ul>
      </div>
    </Accordion>
  {/each}
</div>

<style>
  .dropdown {
    position: absolute;
    top: 110px;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    box-shadow: 0 0 29.7px 0 rgb(0 0 0 / 0.1);
  }

  ul {
    margin: 0;
  }
</style>
