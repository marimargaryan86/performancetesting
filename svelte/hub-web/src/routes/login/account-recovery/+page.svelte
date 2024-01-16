<script lang="ts">
  import { goto } from "$app/navigation";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import routeConfig from "routeConfig";
  import { writable } from "svelte/store";
  import { slideFade } from "transitions/slide-fade";
  import { getPageTitle } from "utils/page-title";

  export let data;

  let errors: string[] = [];
  let info: string[] = [];

  const pending = writable<string | undefined>();

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
      $pending = submitter?.name;

      let reqData = Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>;

      if (submitter) {
        reqData[submitter.name] = submitter.value;
      }

      if (submitter?.name === "email") {
        delete reqData.code;
      }

      const result = await integrationInstancesClient.ory.accountRecovery.complete(reqData);

      if (result.completed) {
        return await goto(routeConfig.routes.account.root, { invalidateAll: true });
      }

      data.flow = result.flow;
      errors = data.flow.ui.messages.filter(({ type }) => type === "error").map(({ text }) => text);
      info = data.flow.ui.messages.filter(({ type }) => type === "info").map(({ text }) => text);
    } finally {
      $pending = undefined;
    }
  }
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Account recovery")}</title>
</svelte:head>

<section class="account-recovery">
  <form on:submit|preventDefault={submit}>
    {#each Object.values(data.flow.ui.groups).flat() as node}
      {#if node.type === "input"}
        {#if node.attributes.type === "hidden"}
          <input type="hidden" value={node.attributes.value} name={node.attributes.name} />
        {:else if node.attributes.type === "email" || node.attributes.type === "text"}
          {@const nodeErrors = node.messages
            .filter(({ type }) => type === "error")
            .map(({ text }) => text)}
          {@const nodeInfo = node.messages
            .filter(({ type }) => type === "info")
            .map(({ text }) => text)}

          <TextField
            autocomplete={node.attributes.autocomplete}
            disabled={node.attributes.disabled}
            required={node.attributes.required}
            label={node.meta.label?.text}
            type={node.attributes.type}
            name={node.attributes.name}
            value={node.attributes.value ?? ""}
            placeholder={node.meta.label?.text ? `Enter ${node.meta.label.text}` : undefined}
            error={nodeErrors.length ? nodeErrors : undefined}
            helpText={nodeInfo.length ? nodeInfo.join(", ") : undefined}
          />
        {:else if node.attributes.type === "submit"}
          <Button type="submit" value={node.attributes.value} name={node.attributes.name}>
            {node.meta.label?.text ?? "Login"}

            {#if $pending === node.attributes.name}
              <LoadingIcon />
            {/if}
          </Button>
        {/if}
      {/if}
    {/each}

    {#if errors.length}
      <div class="errors" typography="body-small" transition:slideFade={{ duration: 300 }}>
        {#each errors as error}
          <span>{error}</span>
        {/each}
      </div>
    {/if}

    {#if info.length}
      <div typography="body-small" transition:slideFade={{ duration: 300 }}>
        {#each info as text}
          <span>{text}</span>
        {/each}
      </div>
    {/if}

    <a class="back" typography="body-medium" href={routeConfig.routes.login.root}>
      Back to login
    </a>
  </form>
</section>

<style>
  .account-recovery > :global(svg) {
    margin-bottom: 60px;
  }

  .account-recovery {
    display: flex;
    flex-flow: column;
    gap: 28px;
    align-items: center;
    width: 100%;
    max-width: 768px;
    padding-left: 16px;
  }

  .errors {
    display: flex;
    flex-flow: column;
    gap: 8px;
    color: var(--color-semantic-error-500);
  }

  form {
    display: inline-flex;
    flex-flow: column;
    gap: 24px;
    width: 100%;
    max-width: 448px;
  }

  .back {
    align-self: flex-end;
    color: var(--color-main-primary-700);
  }
</style>
