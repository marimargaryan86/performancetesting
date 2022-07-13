<script lang="ts">
  import Navigation from "./navigation.svelte";

  export let goToNext: () => void;
  export let goToPrevious: () => void;
</script>

<div class="review">
  <span>Review</span>

  <Navigation {goToNext} {goToPrevious} />
</div>
