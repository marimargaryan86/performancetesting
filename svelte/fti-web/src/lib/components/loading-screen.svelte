<script lang="ts">
  import Spinner from "./spinner.svelte";
</script>

<div class="page">
  <Spinner />
  <span class="searching">Searching...</span>
  <span class="description">Hold on tight, we’re finding the best deals for you</span>
  <div class="loading-items">
    <div class="loading-item">
      <img
        src="/images/loading--luggage-allowance.svg"
        alt="Luggage Allowance"
        class="item-image"
      />
      <span class="item-tag">Generous 23kg luggage allowance</span>
    </div>
    <div class="loading-item">
      <img src="/images/loading--cutting-prices.svg" alt="Cutting Prices" class="item-image" />
      <span class="item-tag">Cutting prices on thousands of packages</span>
    </div>
    <div class="loading-item">
      <img src="/images/loading--different-parts.svg" alt="Different Parts" class="item-image" />
      <span class="item-tag">All parts of your holiday taken care of by us</span>
    </div>
  </div>
</div>

<style>
  :global(.app) {
    background: var(--colours-section-background, #f2fbff);
  }

  .page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh; /* To center the grouping */
  }

  .searching {
    padding-top: 35px;
    color: var(--colours-primary-blue, #01a5c9);
    font-weight: 400;
    font-size: 28px;
    font-family: "Rock Salt", serif;
    text-align: center;
  }

  .description {
    padding-top: 24px;
    color: var(--text-mid, #818181);
    font-weight: 300;
    font-size: 22px;
    font-family: "Plus Jakarta Sans", sans-serif;
    line-height: 48px; /* 218.182% */
    letter-spacing: 0.025rem;
    text-align: center;
  }

  .loading-items {
    display: flex;
    flex-shrink: 0;
    gap: 50px;
    align-items: flex-start;
    padding-top: 88px;
  }

  .loading-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    max-width: 240px;
  }

  .loading-item img {
    width: 234px;
    height: 175px;
  }

  .loading-item span {
    padding-top: 24px;
    color: var(--text-mid, #818181);
    font-weight: 500;
    font-size: 18px;
    text-align: center;
  }
</style>
