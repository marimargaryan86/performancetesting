<script lang="ts">
</script>

<div class="explore-section">
  <div class="tv-number">
    <img class="tv-logo" src="/images/sonnen-logo.png" alt="Sonnen" />
    <p class="tv-title">Got a TV offer number?</p>
    <p class="tv-label">You can watch our TV channel on sonnenklarTV</p>
    <input class="tv-input" type="text" placeholder="E.g: BE3294" />
    <p class="help-label">Need help finding an offer number?</p>
    <button class="find-order">Find Offer</button>
  </div>
  <div class="top-deals">
    <p class="title">Explore our top deals of the week</p>
    <p class="tag">Check out our top deals this week</p>
    <button class="explore-deals">Explore</button>
  </div>
  <div class="holidays">
    <div class="holiday holiday-cruise">
      <p>Packages under €250pp</p>
      <button>Explore</button>
    </div>
    <div class="holiday holiday-inclusive">
      <p>All-inclusive Holidays</p>
      <button>Explore</button>
    </div>
  </div>
</div>

<style>
  .explore-section {
    display: flex;
    gap: 16px;
    align-items: center;
    height: 385px;
    padding: 32px 120px;
  }

  .tv-number {
    flex-basis: 35%;
    height: 344px;
    padding: 20px 32px;
    background: #00a8cd;
    border: 1px solid var(--stroke-colour, #e4e4e4);
    border-radius: 8px;
  }

  .tv-logo {
    width: 100px;
    filter: brightness(0) invert(1);
  }

  .tv-input {
    width: fill-available;
    padding: 18px 16px;
    color: #ffffff;
    font-weight: 500;
    font-size: 18px;
    font-style: normal;
    line-height: normal;
    background: rgb(255 255 255 / 0.25);
    border: 1px solid #ffffff;
    border-radius: 4px;
  }

  .help-label {
    padding: 6px 0;
    color: #ffffff;
    font-weight: 300;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    text-decoration: underline;
  }

  .tv-input::placeholder {
    color: #ffffff;
  }

  .tv-title {
    margin: 0;
    padding-top: 16px;
    color: #ffffff;
    font-weight: 700;
    font-size: 24px;
    font-style: normal;
    line-height: normal;
  }

  .tv-label {
    margin: 16px 0 20px;
    color: white;
  }

  .find-order {
    width: 100%;
    padding: 15px 32px;
    font-weight: 500;
    background: #ffffff;
    border: none;
    border-radius: 4px;
  }

  .top-deals {
    display: flex;
    flex-basis: 35%;
    flex-direction: column;
    height: 320px;
    padding: 32px;
    background: url("/images/top-deals.jpg") no-repeat center center;
    border-radius: 4px;
  }

  .top-deals p {
    margin: 0;
  }

  .top-deals .title {
    padding-bottom: 16px;
    color: #ffffff;
    font-weight: 700;
    font-size: 36px;
    font-style: normal;
    line-height: normal;
  }

  .top-deals .tag {
    flex-grow: 1;
    color: #ffffff;
    font-weight: 300;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
  }

  button {
    padding: 14px 12px;
    background: #ffffff;
    border: none;
    border-radius: 4px;
  }

  .explore-deals {
    align-self: flex-end;
    width: 150px;
    padding: 14px 12px;
    background: #ffffff;
    border: none;
    border-radius: 4px;
  }

  .holidays {
    display: flex;
    flex-basis: 25%;
    flex-direction: column;
    gap: 16px;
    height: 100%;
  }

  .holiday {
    display: flex;
    flex-direction: column;
    height: 35.25%;
    padding: 24px 32px;
    border-radius: 4px;
  }

  .holiday p {
    color: #ffffff;
    font-weight: 700;
    font-size: 22px;
    font-style: normal;
    line-height: normal;
  }

  .holiday button {
    align-self: flex-end;
    padding: 12px 16px;
  }

  .holiday-cruise {
    background: url("/images/ocean-cruises.jpeg") no-repeat center center;
    background-size: cover;
  }

  .holiday-inclusive {
    background: url("/images/inclusive-holidays.jpeg") no-repeat center center;
    background-size: cover;
  }
</style>
