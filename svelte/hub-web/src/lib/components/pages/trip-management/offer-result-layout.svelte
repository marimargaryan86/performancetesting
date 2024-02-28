<script lang="ts">
  import Countdown from "./book/countdown.svelte";
  import BookingLayout from "./booking-layout.svelte";

  export let showActions = false;
  export let pageTitle: string;
  export let pageSubTitle: string;
  export let expiresAt: Date;
  export let showCountdown: boolean;
</script>

<BookingLayout {showActions} {pageTitle} {pageSubTitle}>
  <div class="search-drawer">
    <slot name="search-drawer" />
  </div>

  <div class="content">
    <Countdown {expiresAt} type="offer-search" show={showCountdown} />

    <div class="scroll">
      <div class="search-options">
        <slot name="search-options" />
      </div>

      <slot />
    </div>
  </div>

  <slot name="actions" slot="actions" />
</BookingLayout>

<style>
  .search-drawer {
    position: relative;
    background-color: #ffffff;
    border-top: var(--color-common-line-soft) 1px solid;
  }

  .search-drawer::after {
    position: absolute;
    top: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(180deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .content {
    --options-width: 240px;
    --result-width: calc(1152px - var(--options-width) - 72px);

    display: flex;
    flex-flow: column;
    flex-grow: 1;
    width: 100%;
    padding-top: 24px;
    overflow: auto;
  }

  .content > :global(.countdown) {
    max-width: 1104px;
    margin: 0 24px 24px;
  }

  .scroll {
    display: flex;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    padding: 0 24px;
    overflow: auto;
  }

  .search-options {
    position: sticky;
    top: 0;
    left: 0;
    flex-shrink: 0;
    width: var(--options-width);
  }
</style>
