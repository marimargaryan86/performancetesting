<script lang="ts" context="module">
  function getPassengerLabel(
    passenger: MobileSchemas.OrderPassenger,
    createdAt: Date,
    translator: Translator,
  ): string {
    const age = getAge(passenger.birthDate, createdAt);
    const def = objectExt.entries(PASSENGER_DEFINITIONS).find(([, val]) => {
      if (val.span.from <= age) {
        return age <= (val.span.to ?? Number.MAX_SAFE_INTEGER);
      }

      return false;
    });

    return def ? getPassengerFullLabel(def[0], translator) : translator("words.unknown");
  }
</script>

<script lang="ts">
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { getAge } from "$lib/utils/date-time";
  import { PASSENGER_DEFINITIONS, getPassengerFullLabel } from "$lib/models/passenger";
  import { getTranslator, type Translator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";
  import objectExt from "$lib/object-ext";

  export let passengers: MobileSchemas.OrderPassenger[];
  export let orderCreatedAt: Date = new Date();

  const t = getTranslator();
</script>

<ul class="passengers">
  <li typography="body-large" weight="bold">{$t("words.passengerDetails")}</li>
  {#each passengers as passenger}
    <li class="passenger" typography="body-large">
      <span class="circle">
        <Icon variant="passenger" size="20px" color="var(--color-main-primary-600" />
      </span>
      <strong weight="bold">{passenger.firstName} {passenger.lastName}</strong>
      <em>{getPassengerLabel(passenger, orderCreatedAt, $t)}</em>
    </li>
  {/each}
</ul>

<style>
  .passengers {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .passenger {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 16px;
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 6px;
  }

  em {
    color: var(--color-main-neutral-600);
  }

  .circle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-600) 1px solid;
    border-radius: 50%;
  }
</style>
