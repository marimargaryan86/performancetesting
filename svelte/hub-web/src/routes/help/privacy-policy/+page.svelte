<script lang="ts">
  import { getLocaleData } from "i18n";

  const i18n = getLocaleData();
</script>

<div>
  {#each $i18n.pages.help.pages.privacyPolicy.content as element}
    {#if element.type === "h2"}
      <h2 typography="body-large" weight="bold">{element.html}</h2>
    {:else if element.type === "ul"}
      <ul>
        {#each element.items as item}
          <li>{item}</li>
        {/each}
      </ul>
    {:else if element.type === "p"}
      <p>
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        {@html element.html}
      </p>
    {/if}
  {/each}
</div>

<style>
  div {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  h2 {
    margin-bottom: -8px;
    color: var(--color-main-primary-900);
  }

  div :global(a) {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
