<script lang="ts">
  import github from "$lib/images/github.svg";
  import FaHeart from "svelte-icons/fa/FaHeart.svelte";
  import FaUser from "svelte-icons/fa/FaUser.svelte";
  import FaPhoneAlt from "svelte-icons/fa/FaPhoneAlt.svelte";
  import ExploreDropdown from "./explore-dropdown.svelte";

  let exploreDropdown: boolean = false;

  const setDropdown = (value: boolean): boolean => (exploreDropdown = value);
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
        <a href="/test">Destinations</a>
      </li>
      <li
        on:focus
        on:mouseover={setDropdown.bind(setDropdown, true)}
        on:mouseleave={setDropdown.bind(setDropdown, false)}
      >
        <a href="/test">Holiday types</a>
        {#if exploreDropdown}
          <div class="panel">
            <ExploreDropdown />
          </div>
        {/if}
      </li>
      <li>
        <a href="/test">Offers</a>
      </li>
      <li>
        <a href="/test">Hotels</a>
      </li>
      <li>
        <a href="/test">Car Rental</a>
      </li>
    </ul>
  </nav>

  <div class="side-buttons">
    <a href="https://github.com/sveltejs/kit">
      <img src={github} alt="GitHub" />
    </a>
    <div class="icon heart-icon">
      <FaHeart />
    </div>
    <div class="icon">
      <FaUser />
    </div>
    <div class="phone-box">
      <div class="icon">
        <FaPhoneAlt />
      </div>
      <p>123-456-7890</p>
    </div>
  </div>
</header>

<style>
  header {
    position: fixed;
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

  .icon:hover {
    cursor: pointer;
  }

  .heart-icon:hover {
    color: red;
  }
</style>
