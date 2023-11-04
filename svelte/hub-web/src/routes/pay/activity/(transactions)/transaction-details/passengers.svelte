<script lang="ts">
  import { yymmdd } from "formatting/date-time";
  import type { OrderPassenger } from "integration/junction-hub-api/schemas/order";

  export let passengers: OrderPassenger[];
</script>

<div class="passengers">
  <h3 class="typography title-medium bold">Passengers</h3>

  <div class="list">
    {#each passengers as passenger}
      <span class="typography body-small subtle">First Name</span>
      <span class="typography body-small subtle">Last Name</span>
      <span class="typography body-small subtle">Gender</span>
      <span class="typography body-small subtle">DOB</span>
      <strong class="typography body-small bold">{passenger.firstName}</strong>
      <strong class="typography body-small bold">{passenger.lastName}</strong>
      <strong class="typography body-small bold">{passenger.gender}</strong>
      <strong class="typography body-small bold">{yymmdd(passenger.birthDate)}</strong>
    {/each}
  </div>
</div>

<style>
  .passengers {
    padding: 24px;
    color: var(--color-main-neutral-800);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  h3 {
    margin-bottom: 24px;
  }

  .list {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px 8px;
  }

  strong {
    margin-bottom: 24px;
  }

  .subtle {
    color: var(--color-main-neutral-500);
  }
</style>
