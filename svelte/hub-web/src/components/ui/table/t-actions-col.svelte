<script lang="ts">
  import TCol from "./t-col.svelte";
</script>

<TCol class="actions-col">
  <div class="actions">
    <slot />
  </div>
</TCol>

<style>
  :global(td.actions-col) {
    --width: 0;

    white-space: nowrap;
  }

  .actions {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
  }
</style>
