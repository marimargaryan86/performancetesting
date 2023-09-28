<script lang="ts">
  import PassengerIcon from "components/icons/passenger-icon.svelte";
  import type { OrderPassengerModel } from "integration/junction-mobile-api/schemas/order";
  import { capitalize } from "utils/common";
  import { getPassengerType } from "utils/passenger";

  export let passengers: OrderPassengerModel[];
</script>

<ul class="passengers">
  <li class="typography body-large bold">Passenger details</li>
  {#each passengers as passenger}
    <li class="passenger typography body-large">
      <span class="circle">
        <PassengerIcon color="var(--color-main-primary-600" />
      </span>
      <strong class="typography bold">{passenger.firstName} {passenger.lastName}</strong>
      <em>{capitalize(getPassengerType(passenger))}</em>
    </li>
  {/each}
</ul>

<style>
  .passengers {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .passenger {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 16px;
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 6px;
  }

  em {
    color: var(--color-main-neutral-600);
  }

  .circle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-600) 1px solid;
    border-radius: 50%;
  }
</style>
