<script lang="ts">
  const twentyFourHoursInMins = 1440;

  export let label;
  export let startTime = 0;
  export let endTime = 1439;
  let formattedStartTime = "00:00";
  let formattedEndTime = "23:59";

  function getTimeFromMins(mins: number): string {
    let hours = Math.trunc(mins / 60);
    let minutes = mins % 60;
    let formattedHours = hours.toString().padStart(2, "0");
    let formattedMinutes = minutes.toString().padStart(2, "0");
    return `${formattedHours}:${formattedMinutes}`;
  }

  $: formattedStartTime = getTimeFromMins(startTime);
  $: formattedEndTime = getTimeFromMins(endTime);

  $: startTime = startTime === twentyFourHoursInMins ? startTime - 1 : startTime;
  $: endTime = endTime === twentyFourHoursInMins ? endTime - 1 : endTime;

  function handleStartTimeChange(event): void {
    if (event.target.value > endTime) {
      endTime = startTime;
    }

    startTime = event.target.value;
  }

  function handleEndTimeChange(event): void {
    if (event.target.value < startTime) {
      startTime = endTime;
    }

    endTime = event.target.value;
  }
</script>

<div>
  <div class="label typography body-small-weight-600">
    <span>{label}</span>
  </div>
  <div class="typography body-small">
    <span>{formattedStartTime} - {formattedEndTime}</span>
  </div>
  <div class="slider">
    <input
      type="range"
      min="0"
      max={twentyFourHoursInMins}
      step="10"
      bind:value={startTime}
      on:input={handleStartTimeChange}
    />
    <input
      type="range"
      min="0"
      max={twentyFourHoursInMins}
      step="10"
      bind:value={endTime}
      on:input={handleEndTimeChange}
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
    background-color: var(--color-primary-50);
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

  .label {
    margin-bottom: 16px;
  }
</style>
