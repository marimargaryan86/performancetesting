<script lang="ts">
  import { dev } from "$app/environment";
  import routeConfig from "routeConfig";
  import { getLocaleData } from "i18n";
  import Button from "components/ui/button.svelte";
  import Card from "components/ui/card.svelte";
  import { getPageTitle } from "utils/page-title";
  import FindTripDialog from "./find-trip-dialog.svelte";
  import TripGraphicOne from "assets/images/trip-graphic-1.png";
  import TripGraphicTwo from "assets/images/trip-graphic-2.png";
  import SearchingGraphic from "assets/images/searching.png";

  const i18n = getLocaleData();

  let findTripDialog: FindTripDialog | undefined;

  function searchOrders(): void {
    alert("To be implemented.");
  }
</script>

<svelte:head>
  <title>{getPageTitle($i18n.title, $i18n.pages.dashboard.title)}</title>
</svelte:head>

<FindTripDialog bind:this={findTripDialog} on:search={searchOrders} />

<header>
  <h1 typography="headline-medium" weight="bold">{$i18n.pages.dashboard.title}</h1>
</header>
<div class="wrapper">
  <div class="dashboard">
    <div class="splash">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html $i18n.pages.dashboard.intro}
    </div>

    <div class="widgets">
      <Card variant="horizontal">
        <div slot="media" class="media trip-graphic">
          <img
            src={TripGraphicOne}
            alt="Depiction of destinations and date range."
            class="trip-graphic-1"
          />
          <img src={TripGraphicTwo} alt="Depiction of ticket prices." class="trip-graphic-2" />
        </div>
        <div slot="content" class="content">
          <h3 typography="headline-small" weight="bold">{$i18n.words.bookTrip}</h3>
          <p typography="label-large">{$i18n.sentences.bookTrip}</p>
        </div>
        <div slot="actions" class="actions">
          <Button class="widget-button" href={routeConfig.routes.tripManagement.routes.book.root}
            >{$i18n.actions.bookTrip}</Button
          >
        </div>
      </Card>

      {#if dev}
        <Card variant="horizontal" theme="dark">
          <div slot="media" class="media searching-graphic-wrapper">
            <img
              src={SearchingGraphic}
              alt="Traveler searching with binoculars."
              class="media searching-graphic"
            />
          </div>
          <div slot="content" class="content alt">
            <h3 typography="headline-small" weight="bold">{$i18n.words.manageTrip}</h3>
            <p typography="label-large">{$i18n.sentences.manageTrip}</p>
          </div>
          <div slot="actions" class="actions alt">
            <Button variant="outline" class="widget-button" on:click={findTripDialog?.open}
              >{$i18n.actions.findTrip}</Button
            >
          </div>
        </Card>
      {/if}
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
    grid-template-columns: repeat(auto-fit, 564px);
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

  .media.searching-graphic-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .searching-graphic {
    width: 178px;
    height: 192px;
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
