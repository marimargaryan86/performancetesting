<script lang="ts">
  import { createSlider, melt } from "@melt-ui/svelte";
  const {
    elements: { root, range, thumbs },
    states: { value },
  } = createSlider({
    defaultValue: [0],
    min: 0,
    max: 3000,
    step: 1,
  });

  // eslint-disable-next-line no-warning-comments
  // TODO(2024-03-06): This was a fix I discussed with @mekwall as ts2554 was being thrown
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatValue = (budget: any): string =>
    `${budget.toLocaleString("en", { useGrouping: true })}`;
</script>

<div class="budget-slider-container">
  <span>How much would you like to spend per person?</span>
  <div class="budget-box">
    <span>€{formatValue($value)}</span>
  </div>

  <span use:melt={$root} class="slider">
    <span class="black-bar">
      <span use:melt={$range} class="bar-white" />
    </span>

    {#each $thumbs as thumb}
      <span use:melt={thumb} class="thumb" />
    {/each}
  </span>
  <div class="labels">
    <span>€0</span>
    <span>€1,500</span>
    <span>€3,000</span>
  </div>
</div>
<div class="find-perfect-holiday-container">
  <button class="find-perfect-holiday">Find my perfect holiday 🏝️</button>
</div>

<style>
  .budget-slider-container {
    display: flex;
    flex-direction: column;
    gap: 28px;
    align-items: center;
    width: 55%;
    margin-top: 48px;
    padding: 26px 32px 40px;
    background: rgb(207 207 207 / 0.5);
    border-radius: 10px;
    backdrop-filter: blur(23.75px);
  }

  .budget-slider-container span {
    color: #ffffff;
    font-weight: 500;
    font-size: 24px;
    text-align: center;
  }

  .budget-box {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 208px;
    height: 76px;
    border: 1px solid #ffffff;
    border-radius: 8px;
  }

  .budget-box span {
    margin: 0;
    color: #ffffff;
    font-weight: 800;
    font-size: 40px;
    text-align: center;
  }

  .bar-white {
    height: 8px;
    background: var(--colours-primary-orange);
    opacity: 1;
  }

  .slider {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    height: 20px;
  }

  .black-bar {
    width: 100%;
    height: 8px;
    background: white;
    opacity: 0.8;
  }

  .thumb {
    width: 12px;
    height: 12px;
    background: var(--colours-primary-orange);
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 0 4px rgb(0 0 0 / 0.25);
  }

  .thumb:focus {
    outline: none;
  }

  .labels {
    display: flex;
    justify-content: space-between;
    width: 100%;
    margin-top: 8px;
  }

  .labels span {
    color: #ffffff;
    font-weight: 500;
    font-size: 16px;
  }

  .find-perfect-holiday-container {
    margin-top: 40px;
  }

  .find-perfect-holiday {
    padding: 20px 36px;
    color: #000000;
    font-weight: 600;
    font-size: 18px;
    text-align: center;
    background: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 8px;
  }

  .find-perfect-holiday:hover {
    cursor: pointer;
  }

  @media only screen and (width <= 720px) {
    .find-perfect-holiday {
      padding: 16px 24px;
      font-size: 16px;
    }

    .budget-slider-container span {
      font-size: 18px;
    }
  }
</style>
