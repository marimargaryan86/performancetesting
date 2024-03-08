<script lang="ts">
  import FaHeart from "svelte-icons/fa/FaHeart.svelte";
  import FaUser from "svelte-icons/fa/FaUser.svelte";
  import FaPhoneAlt from "svelte-icons/fa/FaPhoneAlt.svelte";
  import ExploreDropdown from "./explore-dropdown.svelte";
  import FaBars from "svelte-icons/fa/FaBars.svelte";

  let exploreDropdown: boolean = false;

  const setDropdown = (value: boolean): boolean => (exploreDropdown = value);
  function toggleMenu(): void {
    mobileExpand = !mobileExpand;
  }

  let mobileExpand: boolean = false;
</script>

<header>
  <div class="corner">
    <a href="/">
      <img src="/icons/bigxtra-logo.svg" alt="SvelteKit" />
    </a>
  </div>
  <nav>
    <ul>
      <li>
        <a href="/coming-soon">Destinations</a>
      </li>
      <li
        on:focus
        on:mouseover={setDropdown.bind(setDropdown, true)}
        on:mouseleave={setDropdown.bind(setDropdown, false)}
      >
        <a href="/coming-soon">Holiday types</a>
        {#if exploreDropdown}
          <div class="panel">
            <ExploreDropdown />
          </div>
        {/if}
      </li>
      <li>
        <a href="/coming-soon">Offers</a>
      </li>
      <li>
        <a href="/coming-soon">Hotels</a>
      </li>
      <li>
        <a href="/coming-soon">Car Rental</a>
      </li>
    </ul>
  </nav>

  <div class="side-buttons">
    <div class="icon heart-icon">
      <a href="/coming-soon">
        <FaHeart />
      </a>
    </div>
    <div class="icon user-icon">
      <a href="/coming-soon">
        <FaUser />
      </a>
    </div>
    <div class="phone-box">
      <div class="icon">
        <FaPhoneAlt />
      </div>
      <p>123-456-7890</p>
    </div>
    <div class="expand-menu">
      <button class="icon" on:click={toggleMenu}>
        <FaBars />
      </button>
    </div>
  </div>
</header>

{#if mobileExpand}
  <div class="mobile-menu">
    <nav>
      <ul>
        <li>
          <a href="/coming-soon">Destinations</a>
        </li>
        <li>
          <a href="/coming-soon">Holiday types</a>
        </li>
        <li>
          <a href="/coming-soon">Offers</a>
        </li>
        <li>
          <a href="/coming-soon">Hotels</a>
        </li>
        <li>
          <a href="/coming-soon">Car Rental</a>
        </li>
      </ul>
    </nav>
  </div>
{/if}

{#if mobileExpand}
  <div class="mobile-menu">
    <nav>
      <ul>
        <li>
          <a href="/coming-soon">Destinations</a>
        </li>
        <li>
          <a href="/coming-soon">Holiday types</a>
        </li>
        <li>
          <a href="/coming-soon">Offers</a>
        </li>
        <li>
          <a href="/coming-soon">Hotels</a>
        </li>
        <li>
          <a href="/coming-soon">Car Rental</a>
        </li>
      </ul>
    </nav>
  </div>
{/if}

<style>
  header {
    /* position: fixed; */
    left: 10%;
    z-index: 9;
    display: flex;
    justify-content: space-between;
    width: 80%;
    margin: 0 auto;
    padding: 30px 0;
  }

  .corner {
    width: 3em;
    height: 3em;
  }

  nav a {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 0.5rem;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-decoration: none;
    transition: color 0.2s linear;
  }

  .corner a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  .corner img {
    width: 6em;
    height: 3em;
    object-fit: contain;
  }

  nav {
    display: flex;
    justify-content: center;

    --background: rgb(255 255 255 / 0.7);
  }

  ul {
    position: relative;
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: center;
    height: 3em;
    margin: 0;
    padding: 0;
    list-style: none;
    background-size: contain;
  }

  li {
    position: relative;
    height: 100%;
  }

  a:hover {
    color: var(--color-theme-1);
  }

  .panel {
    position: absolute;
    left: -445px;
    z-index: 9999;

    /* width: 1100px; */
    padding: 20px;
    background: white;
  }

  .side-buttons {
    display: flex;
    gap: 30px;
    align-items: center;
    width: auto;
    height: auto;
  }

  .phone-box {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 16px 18px;
    color: white;
    border: 1px solid white;
  }

  .phone-box p {
    margin: 0;
  }

  .icon {
    width: 16px;
    height: 16px;
    color: white;
  }

  .user-icon a {
    color: white;
  }

  .icon:hover {
    cursor: pointer;
  }

  .heart-icon:hover {
    color: red;
  }

  .expand-menu {
    display: none;
  }

  .expand-menu button {
    width: 16px;
    height: 16px;
    padding: 0;
    background: none;
    border: none;
  }

  .mobile-menu {
    display: none;
  }

  @media only screen and (width <= 720px) {
    /* Styles for screens smaller than iPhone X */
    nav,
    .phone-box,
    .heart-icon {
      display: none;
    }

    .expand-menu {
      display: flex;
    }

    .mobile-menu {
      position: absolute;
      right: 0;
      display: block;
      width: 300px;
      height: 100vh;
      background: white;
    }

    header {
      left: 0;
      width: 100%;
    }

    .corner {
      padding-left: 50px;
    }

    .side-buttons {
      padding-right: 20px;
    }

    /* Add your styles here */
  }

  @media only screen and (width <= 430px) {
    /* Styles for screens smaller than iPhone X */
    nav,
    .phone-box,
    .heart-icon {
      display: none;
    }

    .expand-menu {
      display: flex;
    }

    .mobile-menu {
      position: absolute;
      right: 0;
      display: block;
      width: 300px;
      height: 100vh;
      background: white;
    }

    header {
      left: 0;
      width: 100%;
    }

    .corner {
      padding-left: 50px;
    }

    .side-buttons {
      padding-right: 20px;
    }

    /* Add your styles here */
  }
</style>
