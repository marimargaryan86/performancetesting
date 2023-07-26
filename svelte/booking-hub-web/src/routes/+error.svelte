<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import { page } from "$app/stores";
  import Button from "components/ui/button.svelte";

  function reload(): void {
    invalidateAll();
  }
</script>

<main>
  {#if $page.status === 500}
    <h1 class="typography headline-medium">Oops, something went wrong :(</h1>
    <Button on:click={reload}>Reload the page</Button>
  {:else}
    <h1 class="typography headline-medium">{$page.error?.message}</h1>
  {/if}
</main>

<style>
  main {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
  }
</style>
