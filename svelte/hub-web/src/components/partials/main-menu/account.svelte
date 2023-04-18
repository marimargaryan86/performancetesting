<script lang="ts">
  import md5 from "md5";
  import type { UserModel } from "models/user";

  export let user: UserModel;
  export let transitionTimeMs: number;
  export let expanded: boolean;

  $: gravatarHash = md5(user.email.trim().toLowerCase());
</script>

<div class="account" style:--transition-time="{transitionTimeMs}ms" class:expanded>
  <img src="https://www.gravatar.com/avatar/{gravatarHash}?s=40&d=retro" alt="" />

  <div class="info">
    <strong class="ellipsis typography body-small bold">{user.name}</strong>
    <span class="ellipsis typography body-small">{user.email}</span>
  </div>
</div>

<style>
  .account {
    display: flex;
    gap: 12px;
    width: 100%;
  }

  img {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }

  .info {
    width: calc(100% - 52px);
    color: var(--color-neutral-800);
    transition: opacity var(--transition-time) ease;
  }

  .info > strong {
    color: var(--color-common-light-strong);
  }

  .info > span {
    color: var(--color-common-light-medium);
  }

  .info > * {
    display: block;
    width: 100%;
  }

  .account:not(.expanded) > .info {
    opacity: 0;
  }

  .account:not(.expanded) > img {
    margin-left: -1px;
  }
</style>
