<script lang="ts">
  import Car from "./car.svelte";
  import Rail from "./rail.svelte";

  export let data;
</script>

{#if data.searchType === "rail"}
  <Rail bind:data />
{:else if data.searchType === "car"}
  <Car bind:data />
{/if}
