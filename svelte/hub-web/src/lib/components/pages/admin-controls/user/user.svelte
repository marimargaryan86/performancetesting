<script lang="ts">
  import type { MaybePromise } from "@sveltejs/kit";
  import integrationInstancesClient from "~/integration-instances-client";
  import * as OrySchemas from "~/integration/ory/schemas";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getTranslator } from "$lib/i18n";
  import TextField from "$lib/components/ui/text-field.svelte";
  import RoleOption from "./role-option.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { writable } from "svelte/store";
  import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import type { BreadCrumb } from "$lib/models/ui";
  import DeleteUserDialog from "$lib/components/pages/admin-controls/user/delete-user-dialog.svelte";
  import DiscardUserChangesDialog from "$lib/components/pages/admin-controls/user/discard-user-changes-dialog.svelte";
  import { goto } from "$app/navigation";
  import routeConfig from "$lib/route-config";
  import { addToast } from "$lib/components/ui/toaster.svelte";
  import AutocompleteField from "$lib/components/ui/autocomplete-field.svelte";

  export let mode: "create" | "update";
  export let user: HubSchemas.User | HubSchemas.UserPut | undefined;
  export let breadCrumbs: BreadCrumb[];
  let deleteUserDialog: DeleteUserDialog;
  let deleteUser: OrySchemas.User | undefined;
  let discardUserChangesDialog: DiscardUserChangesDialog;

  const t = getTranslator();
  const pending = writable(false);

  let formCompleted: boolean = true;
  let selectedReseller: HubSchemas.Reseller | undefined = user?.reseller;
  let selectedRole: OrySchemas.UserRole;

  // TODO(2024-03-06/alvin.s): Re-evaluate reactive var statements when MVP complete.
  $: currentUser = user;
  $: if (mode === "update") {
    deleteUser = user as OrySchemas.User;
  }
  $: i18nTitleString = $t(`pages.adminControls.pages.users.pages.${mode}.title`);
  $: pageTitle = mode === "update" && currentUser ? currentUser.email : i18nTitleString;
  $: selectedRole = mode === "update" ? user?.role || "reseller-user" : "reseller-user";
  $: i18nSuccessMessage = $t("sentences.userChangesSuccess");
  $: i18nPendingMessage = $t("sentences.userCreatePending");
  $: i18nErrorMessage = $t("sentences.userError");
  $: i18nParentReseller = $t("words.parentReseller");
  $: i18nChildReseller = $t("words.childReseller");

  function selectAdminRole(): void {
    selectedRole = "reseller-admin";
  }

  function selectUserRole(): void {
    selectedRole = "reseller-user";
  }

  function navigateToUserRootRoute(): void {
    goto(routeConfig.routes.adminControls.routes.users.root);
  }

  async function submit(): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;

      if (mode === "create") {
        await createUser();
        addToast({
          data: {
            description: i18nPendingMessage,
            type: "pending",
          },
        });
      } else if (mode === "update") {
        await updateUser();
        addToast({
          data: {
            description: i18nSuccessMessage,
            type: "success",
          },
        });
      }

      navigateToUserRootRoute();
    } catch (e) {
      addToast({
        data: {
          description: i18nErrorMessage,
          type: "error",
        },
      });
    } finally {
      $pending = false;
    }
  }

  async function findReseller(name: string): Promise<HubSchemas.Reseller[]> {
    const resp = await integrationInstancesClient.hub.resellers.find({
      filter: { name },
    });

    return resp.data;
  }

  function findResellerQuery(query: string): MaybePromise<HubSchemas.Reseller[]> {
    if (query.length < 3) {
      return new Promise((r) => r([]));
    }

    const lowerCaseQuery = query.toLowerCase();

    return findReseller(lowerCaseQuery);
  }

  function formatResellerOption(reseller?: HubSchemas.Reseller): string {
    if (!reseller) {
      return "";
    }

    let value = reseller.name;

    if (value && reseller?.parentResellers?.data.length === 0) {
      return value.concat(` (${i18nParentReseller})`);
    }

    return value?.concat(` (${i18nChildReseller})`) ?? "--";
  }

  function openDeleteUserDialog(): void {
    deleteUserDialog.open();
  }

  function openDiscardUserChangesDialog(): void {
    discardUserChangesDialog.open();
  }

  async function createUser(): Promise<void> {
    const { email, role } = currentUser as unknown as HubSchemas.UserPut;
    const reseller = selectedReseller;
    const resellerId = selectedReseller?.id || "";

    if (email && email !== "" && role) {
      await integrationInstancesClient.hub.users.create({
        data: { email, role, resellerId, reseller },
      });
    }
  }

  async function updateUser(): Promise<void> {
    const { id, email, role } = currentUser as unknown as HubSchemas.User;
    const reseller = selectedReseller;
    const resellerId = selectedReseller?.id || "";

    if (email && email !== "" && role) {
      await integrationInstancesClient.hub.users.update({
        id,
        data: { email, role, resellerId, reseller },
      });
    }
  }
</script>

<svelte:head>
  <title>
    {getPageTitle(i18nTitleString)}
  </title>
</svelte:head>

{#if mode === "update"}
  <DeleteUserDialog
    maxWidth={"482px"}
    bind:this={deleteUserDialog}
    user={deleteUser}
    on:delete={navigateToUserRootRoute}
  />
{/if}

<DiscardUserChangesDialog maxWidth={"482px"} bind:this={discardUserChangesDialog} />

<StandardLayout {pageTitle} {breadCrumbs}>
  {#if currentUser}
    <div class="body">
      <form class="user-information">
        <div class="section">
          <div class="section-title">
            <span typography="title-medium">{$t("words.profile")}</span>
            <span class="subtitle" typography="body-medium">{$t("actions.enterUserDetails")}</span>
          </div>
          <div class="fields-container">
            <TextField
              label={$t("words.email")}
              required
              placeholder={$t("actions.enterEmail")}
              bind:value={currentUser.email}
            />
          </div>
        </div>

        <div class="section">
          <div class="section-title">
            <span typography="title-medium">{$t("words.role")}</span>
            <span class="subtitle" typography="body-medium">{$t("actions.enterUserRole")}</span>
          </div>
          <div class="role-options-container">
            <RoleOption on:select={selectAdminRole} active={selectedRole === "reseller-admin"}>
              <div slot="media">
                <Icon
                  variant="password-circular"
                  color="var(--color-common-light-strong)"
                  size="32px"
                />
              </div>
              <div slot="content" class="content">
                <span typography="body-large" weight="bold">{$t("words.admin")}</span>
                <span class="role-description" typography="body-small">
                  {$t("sentences.adminRoleDescription")}
                </span>
              </div>
            </RoleOption>
            <RoleOption on:select={selectUserRole} active={selectedRole === "reseller-user"}>
              <div slot="media">
                <Icon
                  variant="user-circular"
                  color="var(--color-common-light-strong)"
                  size="32px"
                />
              </div>
              <div slot="content" class="content">
                <span typography="body-large" weight="bold">{$t("words.user")}</span>
                <span class="role-description" typography="body-small">
                  {$t("sentences.userRoleDescription")}
                </span>
              </div>
            </RoleOption>
          </div>
        </div>

        <div class="section">
          <div class="section-title">
            <span typography="title-medium">{$t("actions.resellersSearch")}</span>
            <span class="subtitle" typography="body-medium">
              {$t("sentences.searchResellers")}
            </span>
          </div>
          <div class="fields-container">
            <AutocompleteField
              label={$t("words.resellers")}
              required
              placeholder={$t("sentences.typeToSearch")}
              bind:value={selectedReseller}
              autocomplete={findResellerQuery}
              formatter={formatResellerOption}
            />
          </div>
        </div>

        {#if mode === "update"}
          <div class="section">
            <div class="section-title">
              <span class="delete-user-title" typography="title-medium"
                >{$t("actions.deleteUser")}</span
              >
              <span class="subtitle" typography="body-medium">
                {$t("sentences.deleteUserInfo")}
              </span>
              <button class="delete-user-btn" variant="text" on:click={openDeleteUserDialog}>
                <Icon variant="user-cross" color="var(--color-semantic-error-500)" size="16px" />
                <p typography="title-small" weight="bold">Delete Account</p>
              </button>
            </div>
          </div>
        {/if}
      </form>
    </div>
  {/if}
</StandardLayout>

<div class="actions">
  <div class="wrapper">
    <button variant="outline" size="small" on:click={openDiscardUserChangesDialog}>
      {$t("actions.cancel")}
    </button>

    <button variant="primary" size="small" on:click={submit} disabled={!formCompleted}>
      {#if currentUser}
        {$t("actions.save")}
      {:else}
        <LoadingIcon size="14px" />
      {/if}
      {#if $pending}
        <LoadingIcon />
      {/if}
    </button>
  </div>
</div>

<style>
  .body {
    overflow: visible;
    background-color: white;
    border-radius: 16px;
  }

  .user-information {
    display: flex;
    flex-direction: column;
    gap: 40px;
    max-width: 2400px;
    padding: 100px 100px 100px 0;
  }

  .user-information :global(.text-field) {
    --label-font-weight: 600;
    --label-font-size: 14px;
    --label-font-family: "Inter";
  }

  .section {
    display: flex;
    justify-content: start;
    padding-left: 100px;
    overflow: fixed;
  }

  .section-title {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 350px;
    padding-bottom: 20px;
    font-weight: 700;
  }

  .role-description {
    display: flex;
    flex-direction: column;
    color: var(--color-common-light-medium);
    font-size: 12px;
  }

  .role-options-container {
    display: flex;
    gap: 24px;
  }

  .fields-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
    min-width: 540px;
  }

  .subtitle {
    color: var(--color-common-light-soft);
  }

  .delete-user-title {
    color: var(--color-semantic-error-500);
  }

  .delete-user-btn {
    width: 180px;
    height: 42px;
    margin-top: 24px;
    color: var(--color-semantic-error-500);
    border: 1px solid var(--color-semantic-error-500);
  }

  .delete-user-btn:hover {
    background-color: var(--color-semantic-error-100);
    cursor: pointer;
  }

  .actions {
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    gap: 8px;
    justify-content: right;
    width: 100%;
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .actions > .wrapper > button {
    width: 140px;
  }

  @media (width <= 1300px) {
    .section {
      flex-direction: column;
    }

    .role-options-container {
      display: flex;
      flex-direction: column;
    }

    @media (width <= 1100px) {
      .fields-container {
        min-width: 250px;
      }

      .section {
        padding-left: 20px;
      }
    }
  }
</style>
