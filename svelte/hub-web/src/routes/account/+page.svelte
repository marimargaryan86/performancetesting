<script lang="ts" context="module">
  import type { UiNodeGroup } from "integration/ory/schemas/ui-node.js";

  function getOnClick(func: string): () => void {
    // eslint-disable-next-line no-eval
    return eval(func);
  }

  function formatGroupName(name: string): string {
    switch (name as UiNodeGroup) {
      case "profile":
        return "General";
      case "code":
        return "Code";
      case "default":
        return "Default";
      case "link":
        return "Link";
      case "lookup_secret":
        return "Backup recovery codes";
      case "password":
        return "Update password";
      case "totp":
        return "Two-factor authentication";
      case "webauthn":
        return "Security keys";
      default:
        return "Unknown";
    }
  }

  const groupOrder: Exclude<UiNodeGroup, "default">[] = [
    "profile",
    "password",
    "lookup_secret",
    "webauthn",
    "totp",
  ];
</script>

<script lang="ts">
  import StandardLayout from "components/page/standard-layout.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatRole } from "formatting/user";
  import userStore from "stores/user-store";
  import { writable } from "svelte/store";
  import integrationInstancesClient from "integration-instances-client";
  import LoadingIcon from "components/icons/loading-icon.svelte";

  export let data;

  const pending = writable<string | undefined>();

  $: ({ default: defaultGroup, ...groups } = data.flow.ui.groups);

  async function submit(
    event: Event & { currentTarget: EventTarget & HTMLFormElement },
  ): Promise<void> {
    if ($pending) {
      return;
    }

    const submitter =
      "submitter" in event && event.submitter instanceof HTMLButtonElement
        ? { name: event.submitter.name, value: event.submitter.value }
        : undefined;

    try {
      $pending = submitter ? `${submitter.name}:${submitter.value}` : "unknown";

      let reqData: Record<string, unknown> = Object.fromEntries(new FormData(event.currentTarget));

      if (submitter) {
        reqData[submitter.name] = submitter.value;
      }

      if (submitter?.name === "email") {
        delete reqData.code;
      }

      data.flow = await integrationInstancesClient.ory.userSettings.complete(reqData);
    } finally {
      $pending = undefined;
    }
  }
</script>

<svelte:head>
  <title>Account settings · Junction Hub</title>
</svelte:head>

<StandardLayout
  pageTitle="Account settings"
  pageSubTitle={`${$userStore.email} (${formatRole($userStore.role)})`}
>
  <div class="container">
    {#each groupOrder as name}
      {@const nodes = groups[name] ?? []}

      <form on:submit|preventDefault={submit}>
        <h2 class="typography headline-small bold">{formatGroupName(name)}</h2>

        {#each [...nodes, ...(defaultGroup ?? [])] as node}
          {#if node.type === "input"}
            {@const nodeError = node.messages
              .filter(({ type }) => type === "error")
              .map(({ text }) => text)}

            {#if node.attributes.type === "hidden"}
              <input type="hidden" value={node.attributes.value} name={node.attributes.name} />
            {:else if node.attributes.type === "email" || node.attributes.type === "text" || node.attributes.type === "password"}
              <TextField
                autocomplete={node.attributes.autocomplete}
                disabled={node.attributes.disabled}
                label={node.meta.label?.text}
                name={node.attributes.name}
                required={node.attributes.required}
                type={node.attributes.type}
                value={node.attributes.value}
                error={nodeError.length ? nodeError : undefined}
              />
            {:else if node.attributes.type === "button" || node.attributes.type === "submit"}
              <Button
                type={node.attributes.type}
                name={node.attributes.name}
                value={node.attributes.value}
                on:click={node.attributes.onclick ? getOnClick(node.attributes.onclick) : undefined}
              >
                {node.meta.label?.text ?? "Click"}

                {#if $pending === `${node.attributes.name}:${node.attributes.value}`}
                  <LoadingIcon />
                {/if}
              </Button>
            {:else}
              <div>{node.attributes.type}</div>
            {/if}
          {:else if node.type === "script"}
            <svelte:element
              this="script"
              async={node.attributes.async}
              crossorigin={node.attributes.crossorigin}
              id={node.attributes.id}
              integrity={node.attributes.integrity}
              nonce={node.attributes.nonce}
              referrerpolicy={node.attributes.referrerPolicy}
              src={node.attributes.src}
              type={node.attributes.type}
            />
          {:else if node.type === "img"}
            <img
              src={node.attributes.src}
              alt={node.meta.label?.text ?? ""}
              height={node.attributes.height}
              width={node.attributes.width}
              id={node.attributes.id}
            />
          {:else if node.type === "text"}
            <div>{node.meta.label?.text}</div>
            <div>{node.attributes.text.text}</div>
          {/if}
        {/each}
      </form>
    {/each}
  </div>
</StandardLayout>

<style>
  .container {
    display: flex;
    flex-flow: column;
    gap: 40px;
    height: 100%;
    padding: 16px 24px;
    overflow: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  form {
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 100%;
    max-width: 400px;
  }
</style>
