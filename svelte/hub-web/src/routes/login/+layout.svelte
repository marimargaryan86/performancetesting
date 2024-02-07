<main>
  <section class="intro">
    <!-- TODO: Add i18n -->
    <h2 typography="display-medium" weight="bold">Your hub for all things travel related</h2>
    <h3 typography="body-large">Junction Hub will be the place to make and view bookings</h3>

    <img src="/images/illustrations/passengers.png" alt="" />
  </section>

  <slot />
</main>

<style>
  main {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    width: 100%;
    height: 100vh;
    padding: 0 16px;
  }

  main::before,
  main::after {
    position: absolute;
    top: 0;
    left: 0;
    display: block;
    height: 100%;
    content: "";
  }

  main::before {
    z-index: -2;
    width: 100%;
    background-color: var(--color-common-dark-strong);
  }

  main::after {
    z-index: -1;
    width: 50%;
    background-color: var(--color-main-primary-50);
  }

  .intro {
    display: flex;
    flex-flow: column;
    gap: 16px;
    justify-self: flex-end;
    width: 100%;
    max-width: 631px;
    padding: 54px 44px;
    color: var(--color-main-neutral-800);
  }

  .intro > img {
    width: 100%;
  }
</style>
