<script lang="ts">
  // import { ChevronRight, ChevronLeft, Calendar } from "$icons/index.js";
  import DatePicker from "components/date-picker.svelte";
  import DateRangePicker from "components/date-range-picker.svelte";

  export let returnTrip: boolean;
</script>

<div class="dropdown">
  {#if returnTrip}
    <DateRangePicker />
  {:else}
    <DatePicker />
  {/if}
</div>

<style>
  .dropdown {
    position: absolute;
    box-shadow: 0px 0px 29.7px 0px rgba(0, 0, 0, 0.1);
    background: #fff;
    top: 110px;
    display: flex;
    flex-direction: column;
    padding: 32px;
  }
</style>
