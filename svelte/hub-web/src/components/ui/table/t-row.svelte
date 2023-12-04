<script lang="ts">
  export let alternatingBackground = true;
</script>

<tr on:click class:alternating-background={alternatingBackground}><slot /></tr>

<style>
  tr {
    background-color: var(--color-common-background-light-main);
  }

  tr.alternating-background:nth-child(even) {
    background-color: #fbfbfb;
  }

  tr:hover {
    background-color: var(--color-main-primary-50);
  }

  tr:not(:hover) > :global(.actions-col > div > .actions:not(.static)) {
    opacity: 0;
    pointer-events: none;
  }
</style>
