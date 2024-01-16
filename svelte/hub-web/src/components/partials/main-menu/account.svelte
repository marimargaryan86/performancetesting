<script lang="ts">
  import { getLocaleData } from "i18n";
  import md5 from "md5";
  import routeConfig from "routeConfig";
  import { getUser } from "utils/permissions";

  export let transitionTimeMs: number;
  export let expanded: boolean;

  const i18n = getLocaleData();
  const user = getUser();

  $: gravatarHash = md5($user.email.trim().toLowerCase());
</script>

<div class="account" style:--transition-time="{transitionTimeMs}ms" class:expanded>
  <a href={routeConfig.routes.account.root}>
    <img src="https://www.gravatar.com/avatar/{gravatarHash}?s=40&d=retro" alt="" />
  </a>

  <div class="info">
    <strong typography="body-small" weight="bold">{$user.email}</strong>
    <span typography="body-small">{$i18n.roles[$user.role]}</span>
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
    color: var(--color-main-neutral-800);
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
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .account:not(.expanded) > .info {
    opacity: 0;
  }
</style>
