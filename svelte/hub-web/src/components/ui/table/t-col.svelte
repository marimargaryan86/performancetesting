<script lang="ts">
  export let maxWidth: string | undefined = undefined;
  export let width: string | undefined = undefined;
</script>

<td style:--max-width={maxWidth} style:--width={width}><slot /></td>

<style>
  td {
    width: var(--width);
    max-width: var(--max-width);
    padding: 16px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    border-bottom: var(--color-main-neutral-50) 1px solid;
  }
</style>
