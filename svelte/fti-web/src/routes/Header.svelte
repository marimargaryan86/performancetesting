<script>
  import logo from "/icons/bigxtra-logo.svg";
  import github from "$lib/images/github.svg";
  import FaHeart from "svelte-icons/fa/FaHeart.svelte";
  import FaUser from "svelte-icons/fa/FaUser.svelte";
  import FaPhoneAlt from "svelte-icons/fa/FaPhoneAlt.svelte";
</script>

<header>
  <div class="corner">
    <a href="https://kit.svelte.dev">
      <img src={logo} alt="SvelteKit" />
    </a>
  </div>

  <nav>
    <!-- Doesn't go anywhere -->
    <!-- <ul>
      <li aria-current={$page.url.pathname === "/" ? "page" : undefined}>
        <a href="/">Destinations</a>
      </li>
      <li aria-current={$page.url.pathname === "/about" ? "page" : undefined}>
        <a href="/about">Holiday types</a>
      </li>
      <li aria-current={$page.url.pathname === "/about" ? "page" : undefined}>
        <a href="/about">Offers</a>
      </li>
      <li aria-current={$page.url.pathname === "/about" ? "page" : undefined}>
        <a href="/about">Hotels</a>
      </li>
      <li aria-current={$page.url.pathname === "/about" ? "page" : undefined}>
        <a href="/about">Car Rental</a>
      </li>
    </ul> -->
  </nav>

  <div class="side-buttons">
    <a href="https://github.com/sveltejs/kit">
      <img src={github} alt="GitHub" />
    </a>
    <div class="icon">
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
    display: flex;
    justify-content: space-between;
    width: 80%;
    margin: 0 auto;
    padding: 30px 0;
    left: 10%;
  }

  .corner {
    width: 3em;
    height: 3em;
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
    --background: rgba(255, 255, 255, 0.7);
  }

  /* ul {
    position: relative;
    padding: 0;
    margin: 0;
    height: 3em;
    display: flex;
    justify-content: center;
    align-items: center;
    list-style: none;
    background-size: contain;
    gap: 16px;
  } */

  /* li {
    position: relative;
    height: 100%;
  }

  li[aria-current="page"]::before {
    --size: 6px;
    content: "";
    width: 0;
    height: 0;
    position: absolute;
    top: 0;
    left: calc(50% - var(--size));
    border: var(--size) solid transparent;
    border-top: var(--size) solid var(--color-theme-1);
  } */

  /* nav a {
    display: flex;
    height: 100%;
    align-items: center;
    padding: 0 0.5rem;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-decoration: none;
    transition: color 0.2s linear;
  } */

  a:hover {
    color: var(--color-theme-1);
  }

  .side-buttons {
    display: flex;
    height: auto;
    width: auto;
    align-items: center;
    gap: 30px;
  }

  .phone-box {
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid white;
    color: white;
    padding: 16px 18px;
  }

  .phone-box p {
    margin: 0;
  }

  .icon {
    width: 16px;
    height: 16px;
    color: white;
  }
</style>
