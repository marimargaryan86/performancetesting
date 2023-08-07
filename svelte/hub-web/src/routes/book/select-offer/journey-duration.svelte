<script lang="ts">
  export let fromJourneyDuration = 2.5;
  export let toJourneyDuration = 5.5;

  const minJourneyDuration = fromJourneyDuration;
  const maxJourneyDuration = toJourneyDuration;

  function handleMinJourneyDurationChange(
    event: Event & { currentTarget: EventTarget & HTMLInputElement },
  ): void {
    if (Number(event.currentTarget.value) > toJourneyDuration) {
      toJourneyDuration = fromJourneyDuration;
    }

    fromJourneyDuration = Number(event.currentTarget.value);
  }

  function handleMaxJourneyDurationChange(
    event: Event & { currentTarget: EventTarget & HTMLInputElement },
  ): void {
    if (Number(event.currentTarget.value) < fromJourneyDuration) {
      fromJourneyDuration = toJourneyDuration;
    }

    toJourneyDuration = Number(event.currentTarget.value);
  }
</script>

<div>
  <div class="typography body-small">
    <span>{fromJourneyDuration} hours - {toJourneyDuration} hours</span>
  </div>

  <div class="slider">
    <input
      type="range"
      min={minJourneyDuration}
      max={maxJourneyDuration}
      step={0.5}
      bind:value={fromJourneyDuration}
      on:input={handleMinJourneyDurationChange}
    />
    <input
      type="range"
      min={minJourneyDuration}
      max={maxJourneyDuration}
      step={0.5}
      bind:value={toJourneyDuration}
      on:input={handleMaxJourneyDurationChange}
    />
  </div>
</div>

<style>
  .slider {
    position: relative;
    width: 100%;
    height: 4px;
    margin-top: 10px;
    margin-bottom: 16px;
  }

  .slider input[type="range"] {
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 4px;
    margin: 0;
    padding: 0;
    background-color: var(--color-main-primary-100);
    border-radius: 2px;
    outline: none;
    appearance: none;
  }

  .slider input[type="range"]::-webkit-slider-thumb {
    position: relative;
    z-index: 1;
    width: 16px;
    height: 16px;
    background-color: var(--color-main-primary-500);
    border-radius: 50%;
    cursor: pointer;
    appearance: none;
  }

  .slider input[type="range"]:last-child {
    background: none;
  }
</style>
