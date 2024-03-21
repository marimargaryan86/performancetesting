<script lang="ts">
  import type { SliderRange } from "$lib/models/common";

  export let range: SliderRange = {
    from: 0,
    to: 100,
  };

  export let value: SliderRange = {
    from: 10,
    to: 40,
  };
</script>

<div class="range-container">
  <div class="sliders_control">
    <input id="from-slider" type="range" min={range.from} max={range.to} bind:value={value.from} />
    <input id="to-slider" type="range" min={range.from} max={range.to} bind:value={value.to} />
  </div>
  <div class="range-labels">
    <span>{range.from}</span>
    <span>{range.to} </span>
  </div>
</div>

<style>
  .range-container {
    position: relative;
    display: flex;
    flex-direction: column;
  }

  input[type="range"]::-webkit-slider-thumb {
    position: relative;
    top: 2px;
    width: 16px;
    height: 16px;
    background-color: var(--colours-primary-blue);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    appearance: none;
    pointer-events: all;
  }

  #to-slider::-webkit-slider-thumb {
    top: 0;
  }

  input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background-color: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 0 1px #c6c6c6;
    cursor: pointer;
    appearance: none;
    pointer-events: all;
  }

  input[type="range"]::-webkit-slider-thumb:hover {
    box-shadow: 0 0 0 6px rgb(0 168 205 / 0.2);
  }

  input[type="range"]::-webkit-slider-thumb:active {
    box-shadow: 0 0 0 6px rgb(0 168 205 / 0.2);
  }

  input[type="range"] {
    position: absolute;
    width: 100%;
    height: 4px;
    background-color: #01a5c9;
    appearance: none;
    pointer-events: none;
  }

  #from-slider {
    z-index: 1;
    height: 0;
  }

  .range-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
</style>
