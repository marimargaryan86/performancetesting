<script lang="ts">
  import { getLocaleData } from "i18n";

  const i18n = getLocaleData();
</script>

<div>
  {#each $i18n.pages.help.pages.termsAndConditions.content as element}
    {#if element.type === "h2"}
      <h2 typography="body-large" weight="bold">{element.html}</h2>
    {:else if element.type === "p"}
      <p>{element.html}</p>
    {:else if element.type === "ul"}
      <ul>
        {#each element.items as item}
          <li>{item}</li>
        {/each}
      </ul>
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
</style>
