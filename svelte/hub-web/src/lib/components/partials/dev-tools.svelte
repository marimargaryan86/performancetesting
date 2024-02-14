<script lang="ts">
  import { Feature, getFeatures, getFeatureTools } from "$lib/utils/feature-flags";
  import { slide } from "svelte/transition";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import { capitalize } from "$lib/utils/common";

  const features = getFeatures();
  const featureTools = getFeatureTools();

  let expanded = false;

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    expanded ? close() : open();
  }

  function toggleFeature(feature: string): void {
    $featureTools.toggleFeature(feature as Feature);
  }
</script>

<div class="dev-tools" class:expanded>
  <button on:click={toggle} class="toggle-btn">
    <ChevronIcon direction={expanded ? "right" : "left"} />
  </button>

  {#if expanded}
    <ul transition:slide={{ axis: "x", duration: 200 }} class="features" typography="body-medium">
      {#each Object.entries($features) as [name, feature]}
        {#if name !== Feature.DEV_TOOLS}
          <li class="feature">
            <label>
              {capitalize(name.replaceAll("-", " "))}

              <input
                type="checkbox"
                on:change={toggleFeature.bind(toggleFeature, name)}
                checked={feature.enabled}
              />
            </label>

            <div class="info">
              <strong typography="body-xsmall">{feature.owner}</strong>
              <p class="dates" typography="body-small">
                <span><em>Release:</em> <em>{feature.releaseDate}</em></span>
                <span><em>Removal:</em> <em>{feature.removalDate}</em></span>
              </p>

              {#if feature.description}
                <p class="description">
                  {feature.description}
                </p>
              {/if}
            </div>
          </li>
        {/if}
      {/each}
    </ul>
  {/if}
</div>

<style>
  .dev-tools {
    position: fixed;
    top: 0;
    right: 0;
    z-index: var(--z-index-overlay);
    height: 100vh;
    padding: 48px 0 16px;
    background-color: var(--color-common-background-light-main);
    user-select: none;
  }

  .dev-tools.expanded {
    padding: 48px 16px 16px;
    box-shadow: 0 0 10px rgb(0 0 0 / 0.2);
  }

  .toggle-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .dev-tools.expanded > .toggle-btn {
    right: unset;
    left: 16px;
  }

  .features {
    display: grid;
    grid-template-columns: 1fr max-content;
    gap: 16px 0;
  }

  .feature {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
    padding: 4px 0;
  }

  .features label {
    display: grid;
    grid-column: 1 / -1;
    grid-template-columns: subgrid;
    white-space: nowrap;
  }

  .info {
    display: flex;
    flex-flow: column;
    grid-column: 1 / -1;
    gap: 8px;
    width: 240px;
  }

  .info > strong {
    color: var(--color-main-neutral-700);
  }

  .dates {
    display: flex;
    flex-flow: column;
    gap: 2px;
  }

  .dates > span {
    display: flex;
    justify-content: space-between;
  }

  .description {
    padding-top: 8px;
    border-top: var(--color-main-neutral-100) 1px solid;
  }

  input {
    cursor: pointer;
  }
</style>
