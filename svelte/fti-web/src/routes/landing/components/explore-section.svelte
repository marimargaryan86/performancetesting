<script lang="ts">
</script>

<div class="explore-section">
  <div class="tv-number">
    <img class="tv-logo" src="/images/sonnen-logo.png" alt="Sonnen" />
    <p class="tv-title">Got a TV order number?</p>
    <p class="tv-label">You can watch our TV channel on sonnenklarTV</p>
    <input class="tv-input" type="text" placeholder="Enter your TV order number" />
    <p class="help-label">Need help finding your order number?</p>
    <button class="find-order">Find Order</button>
  </div>
  <div class="top-deals">
    <p class="title">Explore our top deals of the week</p>
    <p class="tag">Check out our top deals this week</p>
    <button class="explore-deals">Explore</button>
  </div>
  <div class="holidays">
    <div class="holiday holiday--cruise">
      <p>Ocean Cruises</p>
      <button>Explore</button>
    </div>
    <div class="holiday holiday--inclusive">
      <p>All Inclusive</p>
      <button>Explore</button>
    </div>
  </div>
</div>

<style>
  .explore-section {
    display: flex;
    align-items: center;
    padding: 32px 120px;
    gap: 16px;
    height: 385px;
  }
  .tv-number {
    flex-basis: 35%;
    border-radius: 8px;
    border: 1px solid var(--Stroke-colour, #e4e4e4);
    background: #00a8cd;
    padding: 20px 32px;
  }
  .tv-logo {
    width: 100px;
    filter: brightness(0) invert(1);
  }
  .tv-input {
    border-radius: 4px;
    border: 1px solid #fff;
    background: rgba(255, 255, 255, 0.25);
    color: #fff;
    font-size: 18px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    width: -webkit-fill-available;
    padding: 18px 16px;
  }
  .tv-input::placeholder {
    color: #fff;
  }
  .tv-title {
    color: #fff;
    font-size: 24px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
    padding-top: 16px;
  }
  .tv-label {
    color: white;
  }
  .find-order {
    border-radius: 4px;
    font-weight: 500;
    background: #fff;
    border: none;
    padding: 15px 32px;
    width: 100%;
  }
  .top-deals {
    background: url("/images/top-deals.jpg") no-repeat center center;
    flex-basis: 35%;
    padding: 32px;
    height: 320px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
  }
  .top-deals p {
    margin: 0;
  }
  .top-deals .title {
    color: #fff;
    font-size: 36px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
    padding-bottom: 16px;
  }
  .top-deals .tag {
    color: #fff;
    font-size: 16px;
    font-style: normal;
    font-weight: 300;
    line-height: normal;
    flex-grow: 1;
  }
  button {
    border-radius: 4px;
    background: #fff;
    border: none;
    padding: 14px 12px;
  }

  .explore-deals {
    border-radius: 4px;
    background: #fff;
    border: none;
    padding: 14px 12px;
    width: 150px;
    align-self: flex-end;
  }
  .holidays {
    display: flex;
    flex-direction: column;
    flex-basis: 25%;
    gap: 16px;
    height: 100%;
  }
  .holiday {
    height: 35.25%;
    border-radius: 4px;
    padding: 24px 32px;
    display: flex;
    flex-direction: column;
  }

  .holiday p {
    color: #fff;
    font-family: "Plus Jakarta Sans";
    font-size: 28px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
  }
  .holiday button {
    align-self: flex-end;
  }
  .holiday--cruise {
    background: url("/images/ocean-cruises.jpeg") no-repeat center center;
    background-size: cover;
  }
  .holiday--inclusive {
    background: url("/images/inclusive-holidays.jpeg") no-repeat center center;
    background-size: cover;
  }
</style>
