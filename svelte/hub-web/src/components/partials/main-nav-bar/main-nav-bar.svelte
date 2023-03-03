<script lang="ts" context="module">
  import md5 from "md5";
  import Chevron from "assets/icons/chevron.svelte";
  import JunctionLogoDetailed from "assets/icons/junction-logo-detailed.svelte";
  import LogoutIcon from "assets/icons/logout-icon.svelte";
  import Menu from "./menu.svelte";
  import { invalidateAll } from "$app/navigation";

  async function logout(): Promise<void> {
    document.cookie =
      "session-token=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/; secure=true; samesite=none;";
    await invalidateAll();
  }
</script>

<script lang="ts">
  import type { UserModel } from "models/user";

  export let user: UserModel;

  $: avatar = `https://www.gravatar.com/avatar/${md5(user.email.trim().toLowerCase())}?d=identicon`;
</script>

<input type="checkbox" id="main-nav-bar-expanded" checked />

<nav>
  <JunctionLogoDetailed />

  <label for="main-nav-bar-expanded" class="toggle">
    <Chevron />
    <span>Collapse</span>
  </label>

  <Menu />

  <hr />

  <button class="logout" on:click={logout}>
    <LogoutIcon />
    <span>Logout</span>
  </button>

  <section class="account">
    <img src={avatar} alt="" class="avatar" />

    <strong class="name typography body-medium bold ellipsis">John Smith</strong>
    <span class="email typography label-small ellipsis">{user.email}</span>
  </section>
</nav>

<style>
  #main-nav-bar-expanded {
    display: none;
  }

  nav {
    display: flex;
    flex-flow: column;
    width: 53px;
    padding: 12px 12px 16px;
    overflow: hidden;
    background-image: url("/images/background.png");
    background-repeat: no-repeat;
    background-position: bottom center;
    background-size: cover;
    transition: width 300ms ease;
  }

  nav > :global(svg) {
    width: 141px;
    margin-left: 6px;
  }

  nav > :global(svg *) {
    transition: opacity 300ms ease;
  }

  #main-nav-bar-expanded:checked + nav {
    width: 236px;
  }

  #main-nav-bar-expanded:not(:checked) + nav > :global(svg > g > :not(.icon)) {
    opacity: 0;
  }

  .toggle {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    align-self: flex-end;
    justify-content: center;
    height: 28px;
    margin-bottom: 16px;
    padding: 0 14px 0 8px;
    color: var(--color-primary-500);
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 24px;
    letter-spacing: 0.15px;
    border: var(--color-primary-500) 0.5px solid;
    border-radius: 8px;
    cursor: pointer;
  }

  .logout > span {
    text-align: left;
    transition: opacity 300ms ease;
  }

  #main-nav-bar-expanded:not(:checked) + nav .logout > span {
    opacity: 0;
    pointer-events: none;
  }

  #main-nav-bar-expanded:not(:checked) + nav .toggle {
    align-self: center;
    padding: 6px 8px;
  }

  #main-nav-bar-expanded:not(:checked) + nav .toggle > :global(svg) {
    transform: rotateZ(180deg);
  }

  #main-nav-bar-expanded:not(:checked) + nav .toggle > span {
    display: none;
  }

  #main-nav-bar-expanded:not(:checked) + nav > :global(.menu a > span),
  #main-nav-bar-expanded:not(:checked) + nav > :global(.menu label > span) {
    opacity: 0;
    pointer-events: none;
  }

  hr {
    flex-grow: 1;
    margin: 0;
    margin-bottom: 16px;
    border: 0;
    border-bottom: var(--color-neutral-700) 1px solid;
  }

  .logout {
    display: grid;
    grid-template-columns: 29px 1fr;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    height: 40px;
    margin-bottom: 16px;
    color: var(--color-neutral-800);
    font-weight: 600;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 20px;
    letter-spacing: 0.1px;
    background-color: transparent;
    border: 0;
    outline: 0;
    cursor: pointer;
  }

  .logout > :global(svg) {
    width: 20px;
    height: 20px;
  }

  .account {
    display: grid;
    grid-template-rows: max-content max-content;
    grid-template-columns: max-content 1fr;
    gap: 2px 12px;
    color: var(--color-neutral-800);
  }

  .account > .avatar {
    grid-row: 1 / -1;
    grid-column: 1;
    width: 40px;
    height: 40px;
    object-fit: cover;
    object-position: center;
    border-radius: 50%;
    transition: margin-left 300ms ease;
  }

  .account > .name,
  .account > .email {
    transition: opacity 300ms ease;
  }

  .account > .name {
    grid-row: 1;
    grid-column: 2;
  }

  .account > .email {
    grid-row: 2;
    grid-column: 2;
  }

  #main-nav-bar-expanded:not(:checked) + nav .account .avatar {
    margin-left: -6px;
  }

  #main-nav-bar-expanded:not(:checked) + nav .account .email,
  #main-nav-bar-expanded:not(:checked) + nav .account .name {
    opacity: 0;
  }
</style>
