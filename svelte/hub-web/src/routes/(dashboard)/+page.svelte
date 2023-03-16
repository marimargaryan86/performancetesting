<svelte:head>
  <title>Dashboard · Junction Hub</title>
</svelte:head>

<div class="dashboard layout main-content">
  <h1 class="layout page-header">Dashboard</h1>

  <div class="splash">
    <h2>Welcome to</h2>
    <h3>Junction Hub</h3>
  </div>
</div>

<style>
  .splash {
    padding: 20px 33px 63px;
    color: var(--color-generic-white);
    background-image: url("/images/welcome-bg.png");
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;
    border: 1px solid var(--color-generic-white);
    border-radius: 16px;
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
