<script lang="ts">
  import EntityAvatar from "../entity-avatar.svelte";
  import TCol from "./t-col.svelte";

  export let maxWidth: string | undefined = undefined;
  export let companyName: string | undefined = undefined;
</script>

<TCol {maxWidth}>
  {#if companyName}
    <div class="company">
      <EntityAvatar name={companyName} size="24px" />
      <span>{companyName}</span>
    </div>
  {/if}
</TCol>

<style>
  .company {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
  }

  .company > :global(.entity-avatar) {
    flex-shrink: 0;
  }

  .company > span {
    min-width: 0;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
</style>
