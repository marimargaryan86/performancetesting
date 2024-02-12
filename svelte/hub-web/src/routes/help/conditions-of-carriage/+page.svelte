<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import railServices from "~/data/rail-services";

  const t = getTranslator();
</script>

<div>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html $t("pages.help.pages.conditionsOfCarriage.content")}

  <ul>
    {#each railServices as service}
      <li>
        {service.name} (<a href={service.url} target="_blank">{service.link}</a>)
      </li>
    {/each}
  </ul>
</div>

<style>
  div {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 4px;
    padding-left: 16px;
    color: var(--color-main-primary-900);
    list-style-type: disc;
  }

  a {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
