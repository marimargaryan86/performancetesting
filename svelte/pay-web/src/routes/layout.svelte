<script lang="ts">
  import Modal from "$lib/components/modal.svelte";
  import { modal } from "$lib/stores";
  import Header from "./partials/header/header.svelte";
  import MainMenu from "./partials/main-menu.svelte";
</script>

<main>
  <MainMenu />

  <Header>
    <slot name="head" />
  </Header>

  <div class="work-space">
    <slot name="body" />
  </div>

  {#if $modal.status === "open"}
    <Modal title={$modal.title} type={$modal.type} options={$modal.options} />
  {/if}
</main>

<style>
  main {
    background-color: var(--color-light-background);
    display: grid;
    grid-template-columns: 218px 1fr;
    grid-template-rows: max-content 1fr;
    height: 100vh;
  }

  main > :global(.main-menu) {
    grid-row: 1 / -1;
  }

  .work-space {
    overflow: auto;
  }
</style>
