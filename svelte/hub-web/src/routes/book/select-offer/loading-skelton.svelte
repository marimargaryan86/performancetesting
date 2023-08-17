<div class="offer">
  <div class="group">
    <div class="loading top" />
    <div class="info">
      <ul class="legs">
        <li class="leg">
          <div class="route">
            <span class="circle" />
            <span class="loading" />
            <span class="loading" />
            <span class="line" />
            <span class="loading duration" />
            <span />
            <span class="circle" />
            <span class="loading" />
            <span class="loading place" />
          </div>
        </li>
      </ul>
      <div class="price">
        <span>
          <em class="loading from" />
          <strong class="loading from-price" />
        </span>
      </div>
    </div>
  </div>
</div>

<style>
  .top {
    align-self: auto;
    width: 150px;
    height: 24px;
  }

  .duration {
    align-self: center;
    width: 48px;
    height: 16px;
  }

  .place {
    width: 190px;
    height: 16px;
  }

  .from {
    width: 29px;
    height: 12px;
  }

  .from-price {
    width: 34px;
    height: 26px;
  }

  .loading {
    position: relative;
    overflow: hidden;
    background: #cccccc;
    border-radius: 3px;
  }

  .loading::after {
    position: absolute;
    top: 0;
    left: -100px;
    width: 100px;
    height: 100%;
    background: linear-gradient(to right, transparent, rgb(255 255 255 / 0.439), transparent);
    animation: reflect 800ms ease-out infinite;
    content: "";
  }

  @keyframes reflect {
    to {
      left: calc(100% + 100px);
    }
  }

  .offer {
    display: flex;
    flex-flow: column;
    gap: 8px;
    padding: 8px 22px 22px;
    background-color: var(--color-common-background-light-main);
    border: transparent 2px solid;
    border-top-width: 16px;
    border-radius: 16px;
  }

  .group {
    display: flex;
    flex-flow: column;
    gap: 12px;
  }

  .info {
    display: flex;
    gap: 24px;
  }

  .legs {
    flex-grow: 1;
  }

  .route {
    display: grid;
    grid-template-columns: repeat(3, max-content);
    gap: 12px;
    padding: 8px 0;
  }

  .circle {
    display: block;
    width: 16px;
    height: 16px;
    border: var(--color-common-light-strong) 1px solid;
    border-radius: 50%;
  }

  .line {
    display: block;
    justify-self: center;
    width: 1px;
    height: 100%;
    min-height: 40px;
    border-left: var(--color-main-neutral-500) 1px solid;
  }

  .price {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-items: flex-end;
    justify-content: center;
    padding-left: 24px;
    border-left: var(--color-main-neutral-200) 1px solid;
  }

  .price > span {
    display: flex;
    gap: 4px;
    align-items: center;
  }
</style>
