<script lang="ts">
  import { getPageTitle } from "utils/page-title";
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Dashboard")}</title>
</svelte:head>

<div class="dashboard">
  <h1 class="typography headline-medium bold">Dashboard</h1>

  <div class="splash">
    <h2>Welcome to</h2>
    <h3>Junction Hub</h3>
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

  h2 {
    font-weight: 700;
    font-size: 20px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 36px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  h3 {
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
