<div class="loading-skeleton">
  <div class="itinerary">
    <div class="loading date" />

    <div class="legs">
      <span class="waypoint" />
      <span class="loading time" />
      <span class="loading place first" />
      <span class="route" />
      <span class="loading duration" />
      <span />
      <span class="waypoint" />
      <span class="loading time" />
      <span class="loading place" />
    </div>
  </div>

  <div class="summary">
    <div class="price">
      <span class="loading" />
      <strong class="loading" />
    </div>

    <div class="action loading" />
  </div>
</div>

<style>
  .loading-skeleton {
    display: grid;
    grid-template-columns: 1fr max-content;
    gap: 0 16px;
    padding: 16px;
    overflow: hidden;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: transparent 2px solid;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  .itinerary {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }

  .date {
    width: 200px;
    height: 18px;
  }

  .legs {
    display: grid;
    grid-template-columns: max-content max-content 1fr;
    gap: 4px 16px;
    align-items: center;
  }

  .waypoint {
    width: 13px;
    height: 13px;
    border: var(--color-main-neutral-600) 1px solid;
    border-radius: 50%;
  }

  .time,
  .duration {
    width: 40px;
    height: 16px;
  }

  .place {
    width: 140px;
    height: 16px;
  }

  .place.first {
    width: 180px;
  }

  .route {
    justify-self: center;
    width: 1px;
    height: 24px;
    background-color: var(--color-main-neutral-500);
  }

  .summary {
    display: flex;
    flex-flow: column;
    align-items: flex-end;
    justify-content: space-between;
  }

  .price {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .price > span {
    width: 32px;
    height: 12px;
  }

  .price > strong {
    width: 64px;
    height: 24px;
  }

  .action {
    width: 72px;
    height: 32px;
  }

  .loading {
    position: relative;
    overflow: hidden;
    background: var(--color-main-neutral-200);
    border-radius: 3px;
  }

  .loading::after {
    position: absolute;
    top: 0;
    left: -100px;
    width: 100px;
    height: 100%;
    background: linear-gradient(to right, transparent, rgb(255 255 255 / 0.439), transparent);
    animation: reflect 1200ms ease-out infinite;
    content: "";
  }

  @keyframes reflect {
    to {
      left: calc(100% + 100px);
    }
  }
</style>
