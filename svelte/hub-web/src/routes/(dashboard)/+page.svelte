<script lang="ts">
  import { getLocaleData } from "i18n";
  import { getPageTitle } from "utils/page-title";

  const i18n = getLocaleData();
</script>

<svelte:head>
  <title>{getPageTitle($i18n.title, $i18n.pages.dashboard.title)}</title>
</svelte:head>

<div class="dashboard">
  <h1 class="typography headline-medium bold">{$i18n.pages.dashboard.title}</h1>

  <div class="splash">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html $i18n.pages.dashboard.intro}
  </div>
</div>

<style>
  .dashboard {
    align-self: center;
    width: 100%;
    max-width: 1440px;
    height: 100%;
    padding: 16px 24px 24px;
    background: rgb(255 255 255 / 0.4);
    border: var(--color-common-dark-strong) 1px solid;
    border-bottom-width: 0;
    border-radius: 16px 16px 0 0;
    backdrop-filter: blur(8px);
  }

  .splash {
    display: flex;
    flex-flow: column;
    padding: 20px 33px 63px;
    color: var(--color-common-dark-strong);
    background-image: url("/images/welcome-bg.png");
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;
    border: 1px solid var(--color-common-dark-strong);
    border-radius: 16px;
  }

  h1 {
    margin-bottom: 16px;
  }

  .splash > :global(strong) {
    font-weight: 700;
    font-size: 20px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 36px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .splash > :global(span) {
    margin-top: 8px;
    font-weight: 800;
    font-size: 46px;
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 29px;
    letter-spacing: 2.4px;
    text-transform: uppercase;
  }
</style>
