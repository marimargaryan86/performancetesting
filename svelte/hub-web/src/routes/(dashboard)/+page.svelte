<script lang="ts">
  import routeConfig from "$lib/route-config";
  import { getTranslator } from "$lib/i18n";
  import Card from "$lib/components/ui/card.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import FindTripDialog from "$lib/components/modals/find-trip-dialog.svelte";

  const t = getTranslator();

  let findTripDialog: FindTripDialog | undefined;
</script>

<svelte:head>
  <title>{getPageTitle($t("title"), $t("pages.dashboard.title"))}</title>
</svelte:head>

<FindTripDialog bind:this={findTripDialog} />

<header>
  <h1 typography="headline-medium" weight="bold">{$t("pages.dashboard.title")}</h1>
</header>
<div class="wrapper">
  <div class="dashboard">
    <div class="splash">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html $t("pages.dashboard.intro")}
    </div>

    <div class="widgets">
      <Card variant="horizontal">
        <div slot="media" class="media trip-graphic">
          <img
            src="/images/illustrations/trip-graphic-1.png"
            alt="Depiction of destinations and date range."
          />
          <img src="/images/illustrations/trip-graphic-2.png" alt="Depiction of ticket prices." />
        </div>
        <div slot="content" class="content">
          <h3 typography="headline-small" weight="bold">{$t("words.bookTrip")}</h3>
          <p typography="label-large">{$t("sentences.bookTrip")}</p>
        </div>
        <div slot="actions" class="actions">
          <a
            variant="primary"
            class="widget-button"
            href={routeConfig.routes.tripManagement.routes.book.routes.train.root}
          >
            {$t("actions.bookTrip")}
          </a>
        </div>
      </Card>

      <Card variant="horizontal" theme="dark">
        <div slot="media" class="media searching-graphic-wrapper">
          <img src="/images/illustrations/searching.png" alt="" />
        </div>
        <div slot="content" class="content alt">
          <h3 typography="headline-small" weight="bold">{$t("words.manageTrip")}</h3>
          <p typography="label-large">{$t("sentences.manageTrip")}</p>
        </div>
        <div slot="actions" class="actions alt">
          <button variant="outline" class="widget-button" on:click={findTripDialog?.open}>
            {$t("actions.findTrip")}
          </button>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  header {
    display: flex;
    align-items: center;
    justify-content: start;
    height: 128px;
    padding: 0 24px;
  }

  .wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background-color: var(--color-main-neutral-50);
  }

  .dashboard {
    width: 100%;
    max-width: 1440px;
    height: 100%;
    padding: 16px 24px 24px;
    backdrop-filter: blur(8px);
  }

  .splash {
    display: flex;
    flex-flow: column;
    min-width: 480px;
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

  .widgets {
    display: grid;

    /* Scale the widgets to fit the dashboard horizontally for 1280px and above */
    grid-template-columns: repeat(auto-fit, minmax(480px, auto));
    gap: 32px;
    padding: 24px 0;
  }

  .media {
    width: 211px;
    height: 100%;
    border-radius: 0 16px 16px 0;
  }

  .media.trip-graphic {
    display: flex;
    flex-flow: column;
    align-items: flex-end;
    justify-content: space-evenly;
  }

  .media.trip-graphic > img,
  .media.searching-graphic-wrapper > img {
    margin: 16px;
  }

  .media.searching-graphic-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .content {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }

  .content > p {
    color: var(--color-common-light-medium);
  }

  .actions > :global(.widget-button) {
    width: 100%;
  }

  .actions > :global(.widget-button.outline) {
    --background-color: var(--color-common-background-light-main);
    --color: var(--color-main-primary-400);
  }

  .actions > :global(.widget-button.outline):hover {
    --background-color: var(--color-main-primary-700);
    --border-color: var(--color-main-primary-700);
    --color: var(--color-common-dark-strong);
  }
</style>
