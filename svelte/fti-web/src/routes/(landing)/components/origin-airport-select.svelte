<script lang="ts">
  import Accordion from "components/accordion.svelte";
  import type { Place } from "models/common";

  let selectedOrigin: string = "";

  let origins: Place[] = [
    {
      id: "JFK",
      name: "John F. Kennedy International Airport",
      country: "America",
    },
    { id: "LHR", name: "Heathrow Airport", country: "United Kingdom" },
    { id: "HND", name: "Haneda Airport", country: "Japan" },
    {
      id: "SFO",
      name: "San Francisco International Airport",
      country: "America",
    },
    { id: "DXB", name: "Dubai International Airport", country: "UAE" },
    {
      id: "LAX",
      name: "Los Angeles International Airport",
      country: "America",
    },
    { id: "ORD", name: "O'Hare International Airport", country: "America" },
    {
      id: "ATL",
      name: "Hartsfield-Jackson Atlanta International Airport",
      country: "America",
    },
  ];
  let originCategories: Record<string, Place[]> = origins.reduce(
    (acc, origin) => ({
      ...acc,
      [origin.country]: [...(acc[origin.country as keyof typeof acc] || []), origin],
    }),
    {},
  );
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
    box-shadow: 0px 0px 29.7px 0px rgba(0, 0, 0, 0.1);
    background: #fff;
    top: 110px;
    display: flex;
    flex-direction: column;
  }

  ul {
    margin: 0;
  }
</style>
