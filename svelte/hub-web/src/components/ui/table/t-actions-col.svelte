<script lang="ts">
  import TCol from "./t-col.svelte";
</script>

<TCol>
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
