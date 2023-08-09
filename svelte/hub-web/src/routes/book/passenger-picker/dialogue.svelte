<script lang="ts">
  import { scale } from "svelte/transition";
  import PassengerCounter from "./passenger-counter.svelte";

  export let adults = 0;
  export let children = 0;
  export let infants = 0;
</script>

<div class="dialogue" transition:scale={{ duration: 150, start: 0.8 }}>
  <div class="header typography body-xlarge-weight-600">Passengers</div>

  <div class="navigation">
    <PassengerCounter label="Adult" bind:amount={adults} />
    <PassengerCounter label="Children (2-11)" bind:amount={children} />
    <PassengerCounter label="Infants (under 2)" bind:amount={infants} />
  </div>
</div>

<style>
  .dialogue {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 100;
    width: 300px;
    margin-top: 4px;
    padding: 20px;
    color: var(--color-main-neutral-900);
    background: #ffffff;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgb(17 24 39 / 0.05), 0 12px 16px rgb(17 24 39 / 0.1);
    transform-origin: top left;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    white-space: nowrap;
  }

  .navigation {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
</style>
