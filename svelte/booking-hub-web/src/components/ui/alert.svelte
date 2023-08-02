<script lang="ts">
  import RoundCheckIcon from "components/icons/round-check-icon.svelte";
  import CloseIcon from "components/icons/croses-close-icon.svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();
  export let type: "success" | "failed" = "success";

  let expanded = true;
  function close(): void {
    expanded = false;
    dispatch("closeAlert");
  }
</script>

{#if expanded}
  <div class="alert typography body-medium" class:success={type === "success"}>
    <RoundCheckIcon color="var(--color-main-primary-500)" />
    {#if type === "success"}
      <span class="typography bold">Success!</span>
    {/if}
    <slot />
    <div on:click={close}>
      <CloseIcon />
    </div>
  </div>
{/if}

<style>
  .alert {
    display: flex;
    flex-direction: row;
    gap: 8px;
    align-items: center;
    max-height: 62px;
    margin-bottom: 16px;
    padding: 18px;
    background-color: var(--color-semantic-success-100);
    border: 1px solid var(--color-semantic-success-600);
    border-radius: 16px;
  }

  .alert :last-child {
    display: flex;
    margin-left: auto;
    cursor: pointer;
  }
</style>
