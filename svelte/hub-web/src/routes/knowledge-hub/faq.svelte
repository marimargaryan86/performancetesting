<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { getLocaleData } from "i18n";
  import { slideFade } from "transitions/slide-fade";

  const i18n = getLocaleData();

  let expandedIdx: number | undefined;

  function expand(index: number): void {
    expandedIdx = expandedIdx === index ? undefined : index;
  }
</script>

<section>
  <h2 typography="headline-large" weight="bold">{$i18n.pages.knowledgeHub.faq.title}</h2>

  <ol>
    {#each $i18n.pages.knowledgeHub.faq.items as item, idx}
      {@const expanded = expandedIdx === idx}

      <li>
        <div>
          <strong typography="title-medium" weight="bold">
            {idx + 1}. {item.question}
          </strong>

          {#if expanded}
            <p typography="body-large" transition:slideFade={{ duration: 400 }}>
              {item.answer}
            </p>
          {/if}
        </div>

        <button on:click={expand.bind(expand, idx)}>
          <ChevronIcon
            direction={expanded ? "up" : "down"}
            size="32px"
            color="var(--color-main-primary-500)"
          />
        </button>
      </li>
    {/each}
  </ol>
</section>

<style>
  section {
    display: flex;
    flex-flow: column;
    gap: 48px;
    padding-top: 72px;
  }

  h2 {
    text-align: center;
  }

  ol {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  li {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 32px 24px;
    background-color: var(--color-common-background-light-main);
    border-radius: 12px;
  }

  li > div {
    flex-grow: 1;
  }

  li > div > p {
    padding-top: 16px;
    color: var(--color-common-light-medium);
  }

  button {
    height: 24px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  button > :global(svg) {
    vertical-align: top;
  }
</style>
