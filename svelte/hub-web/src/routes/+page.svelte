<section class="dashboard">
  <h1>Dashboard</h1>

  <div class="welcome">
    <span>Welcome to</span>
    <strong>Junction Hub</strong>
  </div>
</section>

<style>
  section {
    max-width: 1024px;
    min-height: calc(100vh - 48px);
    margin: 0 auto;
    padding: 16px 24px;
    background-color: rgb(255 255 255 / 0.4);
    border: var(--color-generic-white) 1px solid;
    border-radius: 16px;
    backdrop-filter: var(--blur-medium);
  }

  h1 {
    margin-bottom: 12px;
    color: var(--color-neutral-800);
    font-weight: 700;
    font-size: 20px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 36px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .welcome {
    min-height: 183px;
    padding: 20px 32px;
    color: var(--color-generic-white);
    background-image: url("/images/baloons.png");
    background-position: center;
    background-size: cover;
    border: var(--color-generic-white) 1px solid;
    border-radius: 16px;
  }

  .welcome > span {
    display: block;
    margin-bottom: 16px;
    font-weight: 700;
    font-size: 19.2px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 29px;
    letter-spacing: 2.4px;
    text-transform: uppercase;
  }

  .welcome > strong {
    font-weight: 800;
    font-size: 46px;
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 1.1;
    letter-spacing: 2.4px;
    text-transform: uppercase;
  }

  @media screen and (max-width: 1024px) {
    section {
      max-width: 500px;
    }
  }
</style>
