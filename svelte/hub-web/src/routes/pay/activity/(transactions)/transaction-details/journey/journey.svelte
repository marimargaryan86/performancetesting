<script lang="ts">
  import Trip from "./trip.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";

  export let booking: TripBooking;

  $: outbound = booking.detailsList?.[0]?.legs[0];
  $: inbound = booking.detailsList?.[0]?.legs[1];
</script>

<div class="journey">
  <h3 class="typography title-medium bold">Trip</h3>

  <div class="content">
    {#if outbound && booking.detailsList?.[0]}
      <Trip
        leg={outbound}
        operator={booking.detailsList[0].operator}
        cabinClass={booking.detailsList[0].cabinClassName}
        direction="Departure"
      />
    {/if}

    {#if inbound && booking.detailsList?.[0]}
      <hr />

      <Trip
        leg={inbound}
        operator={booking.detailsList[0].operator}
        cabinClass={booking.detailsList[0].cabinClassName}
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
