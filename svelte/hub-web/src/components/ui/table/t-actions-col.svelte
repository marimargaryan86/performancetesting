<script lang="ts">
  import TCol from "./t-col.svelte";

  /** Always show the actions, not only on hover */
  let isStatic = false;
  export { isStatic as static };
</script>

<TCol class="actions-col" width="0">
  <div class="actions" class:static={isStatic}>
    <slot />
  </div>
</TCol>

<style>
  .actions {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
  }
</style>
