<script lang="ts" context="module">
  import { flip } from "svelte/animate";
  import { fly } from "svelte/transition";

  export type ToastData = {
    description: string;
    type: "success" | "pending" | "error";
  };

  const {
    elements: { content, description, close },
    helpers,
    states: { toasts },
    actions: { portal },
  } = createToaster<ToastData>();

  export const addToast = helpers.addToast;
</script>

<script lang="ts">
  import { createToaster, melt } from "@melt-ui/svelte";
  import Icon from "../icons/icon.svelte";
</script>

<div class="toast" use:portal>
  {#each $toasts as { id, data } (id)}
    <div
      class="wrapper"
      use:melt={$content(id)}
      animate:flip={{ duration: 500 }}
      in:fly={{ duration: 150, x: "100%" }}
      out:fly={{ duration: 150, x: "100%" }}
    >
      <div class="notification-card">
        <div
          class="icon"
          class:success={data.type === "success"}
          class:pending={data.type === "pending"}
          class:error={data.type === "error"}
        >
          {#if data.type === "success"}
            <Icon
              variant="checked-circular"
              color="var(--color-semantic-success-600)"
              size="20px"
            />
          {:else if data.type === "pending"}
            <Icon variant="clock-filled" color="var(--color-semantic-info-400)" size="22px" />
          {:else if data.type === "error"}
            <Icon variant="alert-disc" color="var(--color-semantic-error-600)" size="24px" />
          {:else}
            <div />
          {/if}
        </div>
        <div class="content">
          <p typography="body-medium" use:melt={$description(id)}>
            {data.description}
          </p>
        </div>
        <div class="action">
          <button class="close" use:melt={$close(id)} aria-label="close notification">
            <Icon variant="close" size="16px" />
          </button>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  .toast {
    position: fixed;
    bottom: 48px;
    left: 272px;
  }

  .wrapper {
    display: flex;
    gap: 24px;
    width: 353px;
    min-height: 72px;
    margin: 8px 0;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 0 0 40px 4px #e0e0e0;
  }

  .notification-card {
    display: flex;
    flex-flow: row;
    align-items: flex-start;
    justify-content: center;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 100%;
    border-radius: 16px 0 0 16px;
  }

  .icon.success {
    background-color: var(--color-semantic-success-100);
  }

  .icon.pending {
    background-color: var(--color-semantic-info-100);
  }

  .icon.error {
    background-color: var(--color-semantic-error-100);
  }

  .content {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 269px;
    height: 100%;
    padding: 8px 16px;
  }

  .action {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    width: 32px;
    height: 100%;
    padding: 16px 0;
  }

  .close {
    width: 20px;
    height: 20px;
    background-color: transparent;
    border: 0;
    border-radius: 4px;
  }

  .close:hover {
    background-color: var(--color-main-neutral-50);
    cursor: pointer;
  }

  .close > :global(.icon) {
    position: relative;
    top: 1px;
    right: 4px;
  }
</style>
