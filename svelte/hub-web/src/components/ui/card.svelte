<script lang="ts">
  export let variant: "vertical" | "horizontal";
</script>

<div
  class="card"
  class:vertical={variant === "vertical"}
  class:horizontal={variant === "horizontal"}
>
  {#if $$slots.media}
    <div
      class="media-wrapper"
      class:vertical={variant === "vertical"}
      class:horizontal={variant === "horizontal"}
    >
      <slot name="media" />
    </div>
  {/if}

  {#if $$slots.content}
    <div
      class="content-wrapper"
      class:vertical={variant === "vertical"}
      class:horizontal={variant === "horizontal"}
    >
      <slot name="content" />
      {#if $$slots.actions}
        <div
          class="actions-wrapper"
          class:vertical={variant === "vertical"}
          class:horizontal={variant === "horizontal"}
        >
          <slot name="actions" />
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .card {
    display: flex;
    gap: 24px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .card.horizontal {
    flex-flow: column wrap;
  }

  .card.vertical {
    flex-flow: row wrap;
    align-content: flex-start;
  }

  .media-wrapper {
    display: flex;
    flex-flow: column wrap;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

  .content-wrapper {
    padding: 0 24px;
  }
</style>
