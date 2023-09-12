<script lang="ts">
  import type { BookingModel } from "integration/junction-client-api/schemas/booking";
  import Trip from "./trip.svelte";

  export let booking: BookingModel;

  $: outbound = booking.details?.legs[0];
  $: inbound = booking.details?.legs[1];
</script>

<div class="journey">
  <h3 class="typography title-medium bold">Trip</h3>

  <div class="content">
    {#if outbound && booking.details}
      <Trip
        leg={outbound}
        operator={booking.details.operator}
        cabinClass={booking.details.cabinClass}
        direction="Departure"
      />
    {/if}

    {#if inbound && booking.details}
      <hr />

      <Trip
        leg={inbound}
        operator={booking.details.operator}
        cabinClass={booking.details.cabinClass}
        direction="Return"
      />
    {/if}
  </div>
</div>

<style>
  .journey {
    display: flex;
    flex-flow: column;
    gap: 24px;
    max-height: 320px;
    padding: 24px;
    overflow: hidden;
    color: var(--color-common-light-strong);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  .content {
    flex-grow: 1;
    margin: 0 -24px -24px;
    padding: 0 24px 24px;
    overflow: auto;
  }

  hr {
    margin: 24px 0;
    border: 0;
    border-bottom: var(--color-main-neutral-400) 1px solid;
  }
</style>
