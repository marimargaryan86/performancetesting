<script lang="ts">
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getTranslator } from "$lib/i18n";
  import { getUser } from "$lib/utils/permissions";
  import TextField from "$lib/components/ui/text-field.svelte";
  import RoleOption from "../components/role-option.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { writable } from "svelte/store";
  import routeConfig from "$lib/route-config";
  import { sleep } from "$lib/utils/common";

  const t = getTranslator();
  const user = getUser();
  const pending = writable(false);

  let formCompleted: boolean = true;

  const resellerOptions: string[] = [
    "Joshua Reuben Castrioty",
    "Nicholas Sparkes Tong",
    "Reuben Joshua Nichols",
  ];

  let selectedRole: string = "user";

  function selectAdminRole(): void {
    selectedRole = "admin";
  }

  function selectUserRole(): void {
    selectedRole = "user";
  }

  async function submit(): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;
      // TODO: submit form data
      await sleep(1000);
    } finally {
      $pending = false;
    }
  }
</script>

<svelte:head>
  <title>
    {getPageTitle($t("pages.adminControls.pages.users.pages.create.title"))}
  </title>
</svelte:head>

<StandardLayout pageTitle={$t("pages.adminControls.pages.users.pages.create.title")}>
  {#if user}
    <div class="body">
      <form class="user-information">
        <div class="section">
          <div class="section-title">
            <span typography="title-medium">Profile</span>
            <span class="subtitle" typography="body-medium">Enter the user’s account details</span>
          </div>
          <div class="fields-container">
            <TextField label="Name" required placeholder="Enter name" />
            <TextField label="Email address" required placeholder="Enter email address" />
          </div>
        </div>

        <div class="section">
          <div class="section-title">
            <span typography="title-medium">Role</span>
            <span class="subtitle" typography="body-medium">Define the role of the user</span>
          </div>
          <div class="role-options-container">
            <RoleOption on:select={selectAdminRole} active={selectedRole === "admin"}>
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
            <RoleOption on:select={selectUserRole} active={selectedRole === "user"}>
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
            />
          </div>
        </div>
      </form>
    </div>
  {/if}
</StandardLayout>

<div class="actions">
  <div class="wrapper">
    <!-- TODO: ADD POPUP DIALOG TO CONFIRM DISCARDING CHANGES AS PER DESIGNS -->
    <a variant="outline" size="small" href={routeConfig.routes.adminControls.routes.users.root}>
      {$t("actions.cancel")}
    </a>

    <button variant="primary" size="small" on:click={submit} disabled={!formCompleted}>
      {#if user}
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

  .actions > .wrapper > button,
  .actions > .wrapper > a {
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
