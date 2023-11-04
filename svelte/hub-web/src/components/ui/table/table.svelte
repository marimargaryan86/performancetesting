<script lang="ts">
  import { scrollLoad, type ScrollLoadFunc } from "directives/scroll-load";
  let className: string | undefined = undefined;

  export { className as class };
  export let loadMore: ScrollLoadFunc | undefined = undefined;
</script>

<div class="table {className ? className : ''}" use:scrollLoad={{ func: loadMore }}>
  <table><slot /></table>
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
</style>
