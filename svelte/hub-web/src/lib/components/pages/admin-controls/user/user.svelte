<script lang="ts">
  import integrationInstancesClient from "~/integration-instances-client";
  import * as OrySchemas from "~/integration/ory/schemas";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getTranslator } from "$lib/i18n";
  import TextField from "$lib/components/ui/text-field.svelte";
  import RoleOption from "./role-option.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { writable } from "svelte/store";
  import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import type { PaginatedData } from "$lib/models/common";
  import type { BreadCrumb } from "$lib/models/ui";
  import DeleteUserDialog from "$lib/components/pages/admin-controls/user/delete-user-dialog.svelte";
  import DiscardUserChangesDialog from "$lib/components/pages/admin-controls/user/discard-user-changes-dialog.svelte";
  import { goto } from "$app/navigation";
  import routeConfig from "$lib/route-config";
  import { addToast } from "$lib/components/ui/toaster.svelte";

  export let mode: "create" | "update";
  export let user: HubSchemas.User | HubSchemas.UserCreate | undefined;
  export let resellers: PaginatedData<HubSchemas.Reseller> | undefined;
  export let breadCrumbs: BreadCrumb[];
  let deleteUserDialog: DeleteUserDialog;
  let deleteUser: OrySchemas.User | undefined;
  let discardUserChangesDialog: DiscardUserChangesDialog;

  const t = getTranslator();
  const pending = writable(false);

  let resellerOptions: HubSchemas.Reseller[];
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
  $: resellerOptions = resellers?.data || [];
  $: i18nSuccessMessage = $t("sentences.userChangesSuccess");
  $: i18nPendingMessage = $t("sentences.userCreatePending");
  $: i18nErrorMessage = $t("sentences.userError");

  function selectAdminRole(): void {
    selectedRole = "reseller-admin";
  }

  function selectUserRole(): void {
    selectedRole = "reseller-user";
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

      goto(routeConfig.routes.adminControls.routes.users.root);
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

  function formatResellerOption(reseller?: HubSchemas.Reseller): string {
    if (!reseller) {
      return "";
    }

    return reseller.name;
  }

  function openDeleteUserDialog(): void {
    deleteUserDialog.open();
  }

  function openDiscardUserChangesDialog(): void {
    discardUserChangesDialog.open();
  }

  async function createUser(): Promise<void> {
    const { email, role } = currentUser as unknown as HubSchemas.UserCreate;
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
  <DeleteUserDialog maxWidth={"482px"} bind:this={deleteUserDialog} user={deleteUser} />
{/if}

<DiscardUserChangesDialog maxWidth={"482px"} bind:this={discardUserChangesDialog} />

<StandardLayout {pageTitle} {breadCrumbs}>
  {#if currentUser}
    <div class="body">
      <form class="user-information">
        <div class="section">
          <div class="section-title">
            <span typography="title-medium">Profile</span>
            <span class="subtitle" typography="body-medium">Enter the user’s account details</span>
          </div>
          <div class="fields-container">
            <TextField
              label="Email address"
              required
              placeholder="Enter email address"
              bind:value={currentUser.email}
            />
          </div>
        </div>

        <div class="section">
          <div class="section-title">
            <span typography="title-medium">Role</span>
            <span class="subtitle" typography="body-medium">Define the role of the user</span>
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
            <span typography="title-medium">Resellers</span>
            <span class="subtitle" typography="body-medium">
              Add or remove resellers of the user
            </span>
          </div>
          <div class="fields-container">
            <SelectField
              required
              label="Resellers"
              placeholder="Add resellers"
              options={resellerOptions}
              formatter={formatResellerOption}
              bind:value={selectedReseller}
            />
          </div>
        </div>

        {#if mode === "update"}
          <div class="section">
            <div class="section-title">
              <span class="delete-user-title" typography="title-medium">Delete User</span>
              <span class="subtitle" typography="body-medium">
                Deleting this account will permanently remove the user from the system.
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
