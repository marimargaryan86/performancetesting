<script lang="ts" context="module">
  export const LIST_USERS_LIMIT = 20;
</script>

<script lang="ts">
  import { createDropdownMenu, melt } from "@melt-ui/svelte";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getTranslator } from "$lib/i18n";
  import { writable } from "svelte/store";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { slideFade } from "$lib/transitions/slide-fade";
  import routeConfig from "$lib/route-config";
  import Icon from "$lib/components/icons/icon.svelte";
  import StatusBadge from "$lib/components/ui/status-badge.svelte";
  import { scrollLoad, type ScrollLoadFunc } from "$lib/directives/scroll-load.js";
  import integrationInstancesClient from "~/integration-instances-client";
  import type * as OrySchemas from "~/integration/ory/schemas";

  const t = getTranslator();
  const pending = writable(false);
  const columns = "repeat(4, minmax(max-content, 1fr)) minmax(160px, 1fr) 1fr";

  export let data;
  let selectedUserId: string = "";

  $: users = data.users.data.flatMap((item) => item);

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.users.cursor) {
      return { depleted: true };
    }

    const resp = await integrationInstancesClient.hub.users.find({
      cursor: data.users.cursor,
      limit: LIST_USERS_LIMIT,
    });

    data.users = {
      cursor: resp.cursor,
      data: [...data.users.data, ...resp.data],
    };

    return { depleted: !resp.cursor };
  };

  const {
    elements: { menu, item, trigger },
  } = createDropdownMenu();

  function setSelectedUserId(user: OrySchemas.User): void {
    selectedUserId = user.id;
  }
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.adminControls.title"),
      $t("pages.adminControls.pages.users.title"),
    )}
  </title>
</svelte:head>

<StandardLayout pageTitle={$t("pages.adminControls.pages.users.title")}>
  <div slot="actions">
    <a
      variant="primary"
      size="small"
      href={routeConfig.routes.adminControls.routes.users.routes.create.root}
    >
      <Icon variant="plus" size="20px" />
      {$t("actions.addUser")}
    </a>
  </div>

  {#if users.length}
    <x-table
      class="users-table"
      use:scrollLoad={{ func: loadMore, pending }}
      style:grid-template-columns={columns}
    >
      <x-thead>
        <x-th>{"Email"}</x-th>
        <x-th>{"Role"}</x-th>
        <x-th>{"Resellers"}</x-th>
        <x-th>{"User Status"}</x-th>
        <x-th></x-th>
      </x-thead>

      {#each users as hubUser}
        <x-tr>
          <x-td>
            {hubUser.email}
          </x-td>
          <x-td>
            {hubUser.role}
          </x-td>
          <x-td>
            {hubUser.resellerId}
            <!-- {hubUser.resellers.map((reseller) => reseller.name).join(", ")} -->
          </x-td>
          <x-td>
            <StatusBadge value={"active"} />
            <!-- {#if hubUser.status === "active"}
                <StatusBadge value={"active"} />
              {:else if hubUser.status === "pending"}
                <StatusBadge value={"pending"} />
              {/if} -->
          </x-td>
          <button
            class="action-btn"
            on:click={setSelectedUserId.bind(setSelectedUserId, hubUser)}
            use:melt={$trigger}>⋮</button
          >
        </x-tr>
      {/each}

      <div class="menu-wrapper" use:melt={$menu}>
        <ul class="menu">
          <li class="menu-item" use:melt={$item}>
            <a
              class="menu-link"
              href={routeConfig.routes.adminControls.routes.users.routes.update.user(selectedUserId)
                .root}
            >
              <Icon variant="edit-user" size="12px" />
              <p typography="body-small">Edit</p>
            </a>
          </li>
          <li class="menu-item" use:melt={$item}>
            <Icon variant="delete-user" size="10px" />
            <p typography="body-small">Delete</p>
          </li>
        </ul>
      </div>

      {#if $pending}
        <x-tloading transition:slideFade={{ duration: 200 }}>
          <LoadingIcon color="var(--color-main-primary-500)" />
        </x-tloading>
      {/if}
    </x-table>
  {:else}
    <div class="not-found-wrapper">
      <div class="not-found-container">
        <img src="/images/illustrations/not-found.png" alt="" />
        <h3 typography="headline-large" weight="bold">{$t("sentences.noTripsFound")}</h3>
        <pre typography="body-large">{$t("sentences.noTripsFoundMessage")}</pre>
      </div>
    </div>
  {/if}
</StandardLayout>

<style>
  .users-table {
    height: 100%;
  }

  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    padding: 0;
    font-size: 16px;
    line-height: 1;
    background-color: transparent;
    border: none;
    cursor: pointer;
  }

  a:not([variant]) {
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  x-td > :global(.status-badge) {
    width: 100%;
  }

  .not-found-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    background-color: var(--color-common-background-light-main);
  }

  .not-found-container {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: center;
    justify-content: center;
  }

  pre {
    color: var(--color-common-light-soft);
    text-align: center;
  }

  .menu-wrapper {
    width: 96px;
    height: 64px;
    padding: 4px 0;
    background-color: var(--color-common-background-light-main);
    border-radius: 8px;
    box-shadow: 0 0 40px 4px #e0e0e0;
  }

  .menu-item {
    display: flex;
    gap: 4px;
    align-items: center;
    justify-content: flex-start;
    padding: 5px 8px;
  }

  .menu-item:hover {
    background-color: var(--color-main-neutral-50);
    cursor: pointer;
  }

  .menu-link {
    display: flex;
    flex-direction: row;
    gap: 4px;
  }

  .menu-link > p {
    color: var(--color-main-neutral-900);
  }
</style>
