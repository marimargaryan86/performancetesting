<script lang="ts">
  import { openPopup } from "$lib/stores";
  import { onMount } from "svelte";
  import Navigation from "./navigation.svelte";

  export let goToPrevious: () => void;

  onMount(async function () {
    openPopup({
      title: "Completed Successfully",
      type: "popup",
      options: {
        message: "Successfully created beneficiary ",
      },
    });
  });
</script>

<div class="complete">
  <span>Completed</span>

  <Navigation {goToPrevious} />
</div>
