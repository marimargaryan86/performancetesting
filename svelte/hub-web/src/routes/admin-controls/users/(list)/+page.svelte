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
  import { scrollLoad, type ScrollLoadFunc } from "$lib/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import type * as OrySchemas from "~/integration/ory/schemas";
  import DeleteUserDialog from "$lib/components/pages/admin-controls/user/delete-user-dialog.svelte";
  import { addToast } from "$lib/components/ui/toaster.svelte";

  const t = getTranslator();
  const pending = writable(false);
  const columns = "repeat(4, minmax(max-content, 1fr)) minmax(160px, 1fr) 1fr";

  export let data;
  let selectedUser: OrySchemas.User | undefined;
  let deleteUserDialog: DeleteUserDialog;

  $: users = data.users.data.flatMap((item) => item);

  const {
    elements: { menu, item, trigger },
  } = createDropdownMenu();

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

  function setSelectedUser(user?: OrySchemas.User): void {
    if (!user) {
      return;
    }

    selectedUser = user;
  }

  function openDeleteUserDialog(): void {
    deleteUserDialog.open();
  }

  function create(): void {
    addToast({
      data: {
        description: "The resource was created!",
        type: "success",
      },
    });

    addToast({
      data: {
        description: "The resource is pending approval.",
        type: "pending",
      },
    });

    addToast({
      data: {
        description:
          "There was an error. Please try again. This is a test message and can be safely ignored in development.",
        type: "error",
      },
    });
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

<DeleteUserDialog maxWidth={"482px"} bind:this={deleteUserDialog} user={selectedUser} />

<StandardLayout pageTitle={$t("pages.adminControls.pages.users.title")}>
  <div slot="actions">
    <div class="header-actions">
      <button variant="primary" size="small" on:click={create}>Notify</button>
      <a
        variant="primary"
        size="small"
        href={routeConfig.routes.adminControls.routes.users.routes.create.root}
      >
        <Icon variant="plus" size="20px" />
        {$t("actions.addUser")}
      </a>
    </div>
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
            on:click={setSelectedUser.bind(setSelectedUser, hubUser)}
            use:melt={$trigger}>⋮</button
          >
        </x-tr>
      {/each}

      {#if selectedUser !== undefined}
        <div class="menu-wrapper" use:melt={$menu}>
          <ul class="menu">
            <li class="menu-item" use:melt={$item}>
              <a
                class="menu-link"
                href={routeConfig.routes.adminControls.routes.users.routes.update.user(
                  selectedUser.id,
                ).root}
              >
                <Icon variant="edit-user" size="12px" />
                <p typography="body-small">Edit</p>
              </a>
            </li>
            <li class="menu-item" use:melt={$item}>
              <button class="menu-link" on:click={openDeleteUserDialog}>
                <Icon variant="delete-user" size="10px" />
                <p typography="body-small">Delete</p>
              </button>
            </li>
          </ul>
        </div>
      {/if}

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

  .header-actions {
    display: flex;
    flex-direction: row;
    gap: 16px;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
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

  button.menu-link {
    width: 100%;
    padding: 0;
    background-color: transparent;
    border: none;
  }

  button.menu-link:hover {
    cursor: pointer;
  }

  .menu-link {
    display: flex;
    flex-direction: row;
    gap: 4px;
    align-items: center;
  }

  .menu-link > p {
    color: var(--color-main-neutral-900);
  }
</style>
