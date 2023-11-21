<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { scrollLoad, type ScrollLoadFunc } from "directives/scroll-load";
  import { writable } from "svelte/store";
  import { slideFade } from "transitions/slide-fade";

  let className: string | undefined = undefined;
  export { className as class };
  export let loadMore: ScrollLoadFunc | undefined = undefined;

  const pending = writable(false);

  $: loadMoreFunc = loadMore ? getLoadMoreFunc(loadMore) : undefined;

  function getLoadMoreFunc(func: ScrollLoadFunc): ScrollLoadFunc {
    return async (): Promise<{ depleted: boolean }> => {
      try {
        $pending = true;

        return await func();
      } finally {
        $pending = false;
      }
    };
  }
</script>

<div class="table {className ? className : ''}" use:scrollLoad={{ func: loadMoreFunc }}>
  <table><slot /></table>

  {#if $pending}
    <div class="pending" transition:slideFade={{ duration: 300 }}>
      <LoadingIcon color="var(--color-main-primary-600)" />
    </div>
  {/if}
</div>

<style>
  .table {
    overflow: auto;
    background-color: var(--color-main-primary-50);
    border-radius: 8px;
  }

  table {
    width: 100%;
  }

  .pending {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 16px;
  }
</style>
