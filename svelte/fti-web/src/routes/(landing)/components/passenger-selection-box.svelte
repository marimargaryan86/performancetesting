<script lang="ts">
  import CountIncrement from "components/count-increment.svelte";
  import type { Passengers } from "models/common";

  export let passengers: Passengers = {
    adults: 1,
    children: 1,
  };
</script>

<div class="dropdown">
  <div class="passenger-selection">
    <div class="passenger-type">
      <p>Adults</p>
    </div>
    <CountIncrement bind:value={passengers.adults} />
  </div>
  <div class="passenger-selection">
    <div class="passenger-type">
      <p>Children</p>
    </div>
    <CountIncrement bind:value={passengers.children} />
  </div>
  <div class="apply-container">
    <button class="apply">Apply</button>
  </div>
</div>

<style>
  .dropdown {
    position: absolute;
    top: 110px;
    left: -36px;
    display: flex;
    flex-direction: column;
    width: 150%;
    padding: 32px;
    background: #ffffff;
    box-shadow: 0 0 29.7px 0 rgb(0 0 0 / 0.1);
  }

  .passenger-selection {
    display: flex;
    justify-content: space-between;
    padding: 10px 20px;
    border-bottom: 1px solid #f2f2f2;
  }

  .passenger-type p {
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 400;
    font-size: 18px;
    font-style: normal;
    line-height: normal;
  }

  .apply-container {
    display: flex;
    flex-shrink: 0;
    gap: 6px;
  }

  .apply {
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 61px;
    padding: 10px;
    color: white;
    background: var(--text-dark-text, #1c1c1c);
    border: none;
  }
</style>
