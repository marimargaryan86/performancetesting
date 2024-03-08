<script lang="ts">
  import type { SelectedDate } from "$lib/models/common";
  import DatePicker from "$lib/components/date-picker.svelte";
  import DateRangePicker from "$lib/components/date-range-picker.svelte";

  export let returnTrip: boolean;
  export let value: SelectedDate;
</script>

<div class="dropdown">
  {#if returnTrip}
    <DateRangePicker bind:selectedDate={value} />
  {:else}
    <DatePicker bind:selectedDate={value} />
  {/if}
</div>

<style>
  .dropdown {
    position: absolute;
    top: 110px;
    display: flex;
    flex-direction: column;
    padding: 32px;
    background: #ffffff;
    box-shadow: 0 0 29.7px 0 rgb(0 0 0 / 0.1);
  }
</style>
