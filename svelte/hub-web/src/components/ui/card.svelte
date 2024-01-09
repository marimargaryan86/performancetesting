<script lang="ts">
  export let variant: "vertical" | "horizontal";
  export let theme: "light" | "dark" = "light";
</script>

<div
  class="card"
  class:vertical={variant === "vertical"}
  class:horizontal={variant === "horizontal"}
  class:dark={theme === "dark"}
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
    --background-color: var(--color-common-background-light-main);

    display: flex;
    gap: 24px;
    background-color: var(--background-color);
    border-radius: 16px;
  }

  .card.horizontal {
    flex-flow: row-reverse;
  }

  .card.vertical {
    flex-flow: column;
    align-content: flex-start;
  }

  .card.dark {
    --background-color: var(--color-main-primary-50);

    background-color: var(--background-color);
  }

  .media-wrapper {
    display: flex;
    flex-flow: column wrap;
    align-items: center;
    justify-content: center;
  }

  .content-wrapper {
    display: flex;
    flex-flow: column;
    gap: 24px;
    justify-content: space-between;
    padding: 24px;
  }

  .content-wrapper.horizontal {
    padding-right: 0;
  }

  .content-wrapper.vertical {
    padding-top: 0;
  }
</style>
