<script lang="ts">
  import TCol from "./t-col.svelte";
</script>

<TCol class="actions-col" width="0">
  <div class="actions">
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
