<script lang="ts">
  import Navigation from "./navigation.svelte";

  export let goToPrevious: () => void;
</script>

<div class="complete">
  <span>Completed</span>

  <Navigation {goToPrevious} />
</div>
