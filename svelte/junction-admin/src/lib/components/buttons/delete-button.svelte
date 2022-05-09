<script lang="ts">
  import RemoveDocumentIcon from "$lib/icons/remove-document-icon.svelte";

  export let tabindex: -1 | 0 = 0;
  export let title: string = undefined;
</script>

<button class="close-button" on:click {title} {tabindex}>
  <RemoveDocumentIcon />
</button>

<style>
  .close-button {
    background-color: var(--color-red);
    border-radius: 4px;
    border: 0;
    cursor: pointer;
    padding: 2px;
    margin: 0;
    fill: var(--color-white);
    height: 24px;
    width: 24px;
  }

  .close-button > :global(svg) {
    vertical-align: top;
    height: 100%;
    width: 100%;
  }
</style>
