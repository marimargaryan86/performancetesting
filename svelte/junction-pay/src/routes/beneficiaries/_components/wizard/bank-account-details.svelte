<script lang="ts">
  import Navigation from "./navigation.svelte";

  export let goToNext: () => void;
  export let goToPrevious: () => void;
</script>

<div class="bank-account-details">
  <span>Bank Account Details</span>

  <Navigation {goToNext} {goToPrevious} />
</div>
