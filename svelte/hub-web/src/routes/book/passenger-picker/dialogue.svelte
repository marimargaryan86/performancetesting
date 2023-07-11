<script lang="ts">
  import { scale } from "svelte/transition";
  import minusIcon from "components/icons/minus-passenger-icon.svelte";
  import plusIcon from "components/icons/plus-passenger-icon.svelte";

  export let adults = 0;
  export let children = 0;
  export let infants = 0;

  function addAdult(): void {
    adults++;
  }
  function minusAdult(): void {
    if (adults === 0) {
      return;
    }
    adults--;
  }
  function addChildren(): void {
    children++;
  }
  function minusChildren(): void {
    if (children === 0) {
      return;
    }
    children--;
  }
  function addInfant(): void {
    infants++;
  }
  function minusInfant(): void {
    if (infants === 0) {
      return;
    }
    infants--;
  }
</script>

<div class="dialogue" transition:scale|local={{ duration: 150, start: 0.8 }}>
  <div class="header typography body-xlarge-weight-600">Passengers</div>
  <div class="navigation">
    <div class="passenger-counter">
      <div class="passenger-type">Adult</div>
      <div class="counter">
        <div class="counter-btn" on:click={minusAdult}>
          <svelte:component this={minusIcon} color="var(--color-common-dark-strong)" />
        </div>
        <div>{adults}</div>
        <div class="counter-btn" on:click={addAdult}>
          <svelte:component this={plusIcon} color="var(--color-common-dark-strong)" />
        </div>
      </div>
    </div>
    <div class="passenger-counter">
      <div class="passenger-type">Children 2-11</div>
      <div class="counter">
        <div class="counter-btn" on:click={minusChildren}>
          <svelte:component this={minusIcon} color="var(--color-common-dark-strong)" />
        </div>
        <div>{children}</div>
        <div class="counter-btn" on:click={addChildren}>
          <svelte:component this={plusIcon} color="var(--color-common-dark-strong)" />
        </div>
      </div>
    </div>
    <div class="passenger-counter">
      <div class="passenger-type">Infants (under 2)</div>
      <div class="counter">
        <div class="counter-btn" on:click={minusInfant}>
          <svelte:component this={minusIcon} color="var(--color-common-dark-strong)" />
        </div>
        <div>{infants}</div>
        <div class="counter-btn" on:click={addInfant}>
          <svelte:component this={plusIcon} color="var(--color-common-dark-strong)" />
        </div>
      </div>
    </div>
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

  .passenger-counter {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .counter-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    background-color: var(--color-main-primary-500);
    border-radius: 8px;
    cursor: pointer;
  }

  .counter-btn:hover {
    background-color: var(--color-main-primary-600);
  }

  .counter {
    display: flex;
    gap: 16px;
    justify-content: space-between;
  }
</style>
