<script lang="ts">
  export let title: string | undefined = undefined;
  export let intro: string;
  export let description: string;
</script>

<div class="section">
  {#if title}
    <h2 typography="headline-small" weight="bold">{title}</h2>
  {/if}

  <div class="layout">
    <aside>
      <h3 typography="title-medium" weight="bold">{intro}</h3>
      <p typography="body-medium">{description}</p>
    </aside>

    <slot />
  </div>
</div>

<style>
  .section {
    display: flex;
    flex-flow: column;
    gap: 40px;
    align-self: center;
    width: 100%;
    max-width: 914px;
    color: var(--color-common-light-strong);
  }

  .layout {
    display: flex;
    gap: 24px;
  }

  aside {
    flex-grow: 1;
  }

  aside > p {
    color: var(--color-common-light-soft);
  }

  .layout > :global(form) {
    display: flex;
    flex-flow: column;
    gap: 24px;
    width: 100%;
    max-width: 540px;
  }

  .layout > :global(form .text-field),
  .layout > :global(form .select-field) {
    --height: 40px;
    --label-font-size: 16px;
    --label-font-weight: 600;
  }
</style>
