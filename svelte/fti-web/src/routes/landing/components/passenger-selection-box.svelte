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
    box-shadow: 0px 0px 29.7px 0px rgba(0, 0, 0, 0.1);
    background: #fff;
    top: 110px;
    display: flex;
    flex-direction: column;
    left: -36px;
    width: 150%;
    padding: 32px;
  }

  .passenger-selection {
    display: flex;
    justify-content: space-between;
    padding: 10px 20px;
    border-bottom: 1px solid #f2f2f2;
  }

  .passenger-type p {
    color: var(--Text-Dark-Text, #1c1c1c);
    font-family: "Plus Jakarta Sans";
    font-size: 18px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  .apply-container {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }

  .apply {
    width: 100%;
    background: var(--Text-Dark-Text, #1c1c1c);
    color: white;
    border: none;
    height: 61px;
    padding: 10px;
    justify-content: center;
    align-items: center;
  }
</style>
